#!/usr/bin/env python3
"""Active-configuration routing tracer for Xilinx 7-series FASM.

Builds the wire-node graph from a prjxray database (tilegrid + tileconn),
adds the *active* PIPs decoded from a FASM file, and reports connected
components / traces between sites. Unlike prjxray simpleroute (which finds
*possible* routes from the full PIP database), this uses only the PIPs that
are actually set in the bitstream, so it reflects the configured design.

This is a first step toward IO-interconnect-aware tracing (IOB <-> fabric)
and EMIO port identification for Zynq, which the current prjxray tooling
does not provide.

Usage:
  route_trace.py --db-root <prjxray-db>/zynq7 --part xc7z020 \
      --fasm design.fasm [--components] [--site RIOB33_X73Y103 ...]
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


def load_db(db_root, part):
    base = os.path.join(db_root, part)
    tilegrid = json.load(open(os.path.join(base, "tilegrid.json")))
    tileconn = json.load(open(os.path.join(base, "tileconn.json")))
    node_wires = json.load(open(os.path.join(base, "node_wires.json")))
    return tilegrid, tileconn, node_wires


# Site-config features have a site (not a wire) as the middle field, e.g.
# RIOI3_X73Y51.OLOGIC_Y1.OQUSED or CLBLM_X0Y0.SLICEL_X0Y0.AFF.ZINI.
# Routing PIPs have wires on both sides, e.g. INT_R_X1Y2.NL1BEG1.SW2END1.
SITE_RE = re.compile(
    r"^(OLOGIC|ILOGIC|IDELAY|ODELAY|SLICE[LM]|SLICEL|SLICEM|BRAM|FIFO|DSP|"
    r"IOB|IDELAYCTRL|BUFG|PLL|MMCM|GTPE2|GTHE2|XADC|SYSMON|EFUSE|USR_ACCESS|"
    r"ICAP|FRAME_ECC|BSCAN|STARTUP|CAPTURE|DCIRESET|DNA_PORT|EMAC|GEM)")


def wire_sets(node_wires):
    pat = node_wires.get("node_pattern_wires", {})
    return {t: set(w) for t, w in pat.items()}


def build_nodes(tilegrid, tileconn):
    """Merge (tile, wire) pairs connected across tiles via tileconn."""
    type_to_tiles = defaultdict(list)
    grid_to_tile = {}
    for tile, td in tilegrid.items():
        type_to_tiles[td["type"]].append(tile)
        grid_to_tile[(td["grid_x"], td["grid_y"])] = tile

    uf = UnionFind()
    for entry in tileconn:
        type_a, type_b = entry["tile_types"]
        dx, dy = entry["grid_deltas"]
        for tile_a in type_to_tiles.get(type_a, []):
            ga = (tilegrid[tile_a]["grid_x"], tilegrid[tile_a]["grid_y"])
            gb = (ga[0] + dx, ga[1] + dy)
            tile_b = grid_to_tile.get(gb)
            if tile_b is None or tilegrid[tile_b]["type"] != type_b:
                continue
            for wa, wb in entry["wire_pairs"]:
                uf.union((tile_a, wa), (tile_b, wb))
    return uf, type_to_tiles, grid_to_tile


PIP_RE = re.compile(r"^([A-Z0-9_]+_X\d+Y\d+)\.([A-Z0-9_]+)\.([A-Z0-9_]+)$")


def active_pip_edges(fasm_path, uf, tilegrid, wiresets):
    """Return (src_node, dst_node, pip_name) for active routing PIPs.

    A 3-part feature TILE.dst.src is a PIP when dst is a routing wire of that
    tile type (per node_pattern_wires), not a site. This includes interconnect
    (INT), IO-interconnect (RIOI3/LIOI3), CLB and PS-boundary tiles, so endpoints
    connect to the fabric backbone.
    """
    edges = []
    with open(fasm_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            feat = line.split()[0]
            m = PIP_RE.match(feat)
            if not m:
                continue
            tile, dst, src = m.groups()
            # Exclude site-config (middle field is a site, not a wire). The
            # db wire lists are incomplete for zynq7, so exclude by site-name
            # pattern rather than requiring wire membership.
            if SITE_RE.match(dst):
                continue
            ttype = tilegrid.get(tile, {}).get("type")
            ws = wiresets.get(ttype)
            if ws is not None and dst in ws:
                pass  # confirmed wire
            edges.append((uf.find((tile, src)), uf.find((tile, dst)), feat))
    return edges


def ppips_edges(db_root, part, uf, type_to_tiles):
    """Fixed 'always' pseudo-PIPs from ppips_*.db (e.g. PS7 EMIO -> PSS LOGIC_OUTS).

    These are hardwired connections not present in the bitstream FASM, but they
    are essential to link PS7 EMIO signal wires to the fabric routing. Format:
    TILETYPE.dst.src always — applies to every tile instance of TILETYPE.
    """
    import glob
    edges = []
    base = os.path.join(db_root, part)
    paths = glob.glob(os.path.join(base, "ppips_*.db"))
    paths += glob.glob(os.path.join(os.path.dirname(base), "ppips_*.db"))
    type_re = re.compile(r"^([A-Z0-9_]+)\.([A-Z0-9_]+)\.([A-Z0-9_]+)$")
    for path in paths:
        with open(path) as f:
            for line in f:
                parts = line.split()
                if len(parts) < 2 or parts[1] != "always":
                    continue
                m = type_re.match(parts[0])
                if not m:
                    continue
                ttype, dst, src = m.groups()
                for tile in type_to_tiles.get(ttype, []):
                    edges.append((uf.find((tile, src)), uf.find((tile, dst)),
                                  parts[0]))
    return edges


def components(edges):
    uf = UnionFind()
    adj = defaultdict(set)
    for s, d, _ in edges:
        uf.union(s, d)
        adj[s].add(d)
        adj[d].add(s)
    comp = defaultdict(list)
    for n in adj:
        comp[uf.find(n)].append(n)
    return uf, adj, comp


def bfs_path(adj, src, dst):
    """Shortest path src->dst through active PIPs, or None if disconnected."""
    if src == dst:
        return [src]
    prev = {src: None}
    queue = [src]
    while queue:
        nxt = []
        for n in queue:
            for m in adj[n]:
                if m in prev:
                    continue
                prev[m] = n
                if m == dst:
                    path = [m]
                    while prev[path[-1]] is not None:
                        path.append(prev[path[-1]])
                    return path[::-1]
                nxt.append(m)
        queue = nxt
    return None


def iomux_edges(fasm_path, uf, tilegrid):
    """Connect IOB sites to the fabric via IOI OLOGIC/ILOGIC mux selections.

    RIOI3_X#Y#.OLOGIC_Y#.OMUX.<src> selects the wire driving an output pin;
    ILOGIC_Y#.IMUX.<src> selects the wire feeding an input pin. The mux input
    name maps to a wire in the same IOI tile, which tileconn merges into the
    interconnect. This is the IOB<->fabric link that INT-only PIP tracing misses.
    """
    edges = []
    mux_re = re.compile(
        r"^((?:RIOI3|LIOI3|RIOI3_TBYTESRC|LIOI3_TBYTETERM)_X\d+Y\d+)\."
        r"(OLOGIC|ILOGIC)_Y(\d+)\.(OMUX|IMUX)\.([A-Z0-9_]+)$")
    with open(fasm_path) as f:
        for line in f:
            feat = line.strip().split()[0] if line.strip() else ""
            m = mux_re.match(feat)
            if not m:
                continue
            tile, logic, y, mux, src = m.groups()
            # mux input wire in the IOI tile (e.g. OLOGIC_Y0 OMUX src -> IOI wire)
            wire = "%s_Y%s_%s_%s" % (logic, y, mux, src)
            node = uf.find((tile, wire))
            site = uf.find((tile, "%s_Y%s" % (logic, y)))
            edges.append((node, site, feat))
    return edges


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db-root", required=True)
    ap.add_argument("--part", required=True)
    ap.add_argument("--fasm", required=True)
    ap.add_argument("--components", action="store_true")
    ap.add_argument("--iomux", action="store_true",
                    help="also add IOI OLOGIC/ILOGIC mux edges (experimental)")
    ap.add_argument("--trace", nargs=2, metavar=("SRC", "DST"),
                    help="BFS trace between two tile/wire nodes")
    ap.add_argument("--site", action="append", default=[],
                    help="report the component containing this tile/wire")
    args = ap.parse_args()

    tilegrid, tileconn, node_wires = load_db(args.db_root, args.part)
    wiresets = wire_sets(node_wires)
    uf, type_to_tiles, grid_to_tile = build_nodes(tilegrid, tileconn)
    edges = active_pip_edges(args.fasm, uf, tilegrid, wiresets)
    edges += ppips_edges(args.db_root, args.part, uf, type_to_tiles)
    if args.iomux:
        edges += iomux_edges(args.fasm, uf, tilegrid)
    print("active routing PIP edges: %d" % len(edges), file=sys.stderr)
    cuf, adj, comp = components(edges)
    print("connected components: %d" % len(comp), file=sys.stderr)

    if args.components:
        sizes = sorted((len(v) for v in comp.values()), reverse=True)
        print("component sizes (top 20):", sizes[:20])
        for root, nodes in sorted(comp.items(), key=lambda kv: -len(kv[1]))[:10]:
            types = defaultdict(int)
            for (tile, wire) in nodes:
                types[tilegrid.get(tile, {}).get("type", "?")] += 1
            top = sorted(types.items(), key=lambda kv: -kv[1])[:6]
            print("  comp size %d: %s" % (len(nodes), top))

    def node_of(s):
        tile, wire = s.split("/")
        return uf.find((tile, wire))

    if args.trace:
        s, d = node_of(args.trace[0]), node_of(args.trace[1])
        path = bfs_path(adj, s, d)
        if path is None:
            print("DISCONNECTED: %s and %s are in different components"
                  % (args.trace[0], args.trace[1]))
            print("  src comp size: %d" % len(comp.get(cuf.find(s), [])))
            print("  dst comp size: %d" % len(comp.get(cuf.find(d), [])))
        else:
            print("CONNECTED, path length %d:" % (len(path) - 1))
            for n in path:
                print("  %s/%s" % n)

    for s in args.site:
        n = node_of(s)
        root = cuf.find(n)
        nodes = comp.get(root, [])
        types = defaultdict(int)
        for (tile, wire) in nodes:
            types[tilegrid.get(tile, {}).get("type", "?")] += 1
        print("site %s: component size %d, types %s"
              % (s, len(nodes), sorted(types.items(), key=lambda kv: -kv[1])[:8]))
        io = sorted({tile for (tile, wire) in nodes
                     if tilegrid.get(tile, {}).get("type", "") in
                     ("RIOI3", "LIOI3", "RIOB33", "LIOB33", "RIOI3_TBYTESRC",
                      "LIOI3_TBYTETERM")})
        if io:
            print("  IO tiles in component: %s" % io)


if __name__ == "__main__":
    main()
