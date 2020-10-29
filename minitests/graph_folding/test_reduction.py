import argparse
from collections import namedtuple
import json
import progressbar
import capnp
import capnp.lib.capnp
capnp.remove_import_hook()
import os.path

from prjxray.node_lookup import NodeLookup

WireToNode = namedtuple(
    'WireToNode', 'wire_in_tile_pkey delta_x delta_y node_wire_in_tile_pkey')
NodeToWire = namedtuple('NodeToWire', 'wire_in_tile_pkey delta_x delta_y')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--database')
    parser.add_argument('--wire_patterns')

    args = parser.parse_args()

    lookup = NodeLookup(database=args.database)
    cur = lookup.conn.cursor()
    cur2 = lookup.conn.cursor()
    cur3 = lookup.conn.cursor()

    wire_to_node_patterns = {}
    tile_nodes_to_wire_patterns = {}

    for tile_pkey, tile_type_pkey, tile_name, tile_x, tile_y in progressbar.progressbar(
            cur.execute("SELECT pkey, tile_type_pkey, name, x, y FROM tile;")):

        wire_to_nodes = []

        for wire_in_tile_pkey, wire_pkey, node_pkey in cur2.execute("""
SELECT wire_in_tile_pkey, wire.pkey, wire.node_pkey
FROM wire
WHERE tile_pkey = ?;
                """, (tile_pkey, )):
            cur3.execute(
                """
SELECT tile.x, tile.y, node.wire_in_tile_pkey
FROM node
INNER JOIN tile ON node.tile_pkey = tile.pkey
WHERE node.pkey = ?;
                """, (node_pkey, ))
            node_tile_x, node_tile_y, node_wire_in_tile_pkey = cur3.fetchone()

            wire_to_nodes.append(
                WireToNode(
                    wire_in_tile_pkey=wire_in_tile_pkey,
                    delta_x=node_tile_x - tile_x,
                    delta_y=node_tile_y - tile_y,
                    node_wire_in_tile_pkey=node_wire_in_tile_pkey))

        key = frozenset(wire_to_nodes)

        if key not in wire_to_node_patterns:
            wire_to_node_patterns[key] = set()

        wire_to_node_patterns[key].add(tile_pkey)

        tile_nodes_to_wires = []
        for node_pkey, node_wire_in_tile_pkey in cur2.execute("""
SELECT node.pkey, node.wire_in_tile_pkey
FROM node
WHERE node.tile_pkey = ?;
            """, (tile_pkey, )):

            node_to_wires = []

            for wire_in_tile_pkey, wire_tile_x, wire_tile_y in cur3.execute("""
SELECT wire.wire_in_tile_pkey, tile.x, tile.y
FROM wire
INNER JOIN tile ON wire.tile_pkey = tile.pkey
WHERE wire.node_pkey = ?;
                """, (node_pkey, )):
                node_to_wires.append(
                    NodeToWire(
                        delta_x=wire_tile_x - tile_x,
                        delta_y=wire_tile_y - tile_y,
                        wire_in_tile_pkey=wire_in_tile_pkey))

            tile_nodes_to_wires.append(
                (node_wire_in_tile_pkey, frozenset(node_to_wires)))

        key = frozenset(tile_nodes_to_wires)

        if key not in tile_nodes_to_wire_patterns:
            tile_nodes_to_wire_patterns[key] = set()

        tile_nodes_to_wire_patterns[key].add(tile_pkey)

    #wire_names = {}
    #for wire_in_tile_pkey, name in cur.execute("SELECT pkey, name FROM wire_in_tile;"):
    #    wire_names[wire_in_tile_pkey] = name

    search_path = []
    for path in ['/usr/local/include', '/usr/include']:
        if os.path.exists(path):
            search_path.append(path)

    wire_patterns_schema = capnp.load('wire_patterns.capnp')
    wire_patterns_capnp = wire_patterns_schema.WirePatterns.new_message()

    dxdys = set()
    for wire_to_nodes in wire_to_node_patterns.keys():
        for _, dx, dy, _ in wire_to_nodes:
            dxdys.add((dx, dy))

    dxdys = sorted(dxdys)
    dxdy_to_dxdy_idx = {}

    wire_patterns_capnp.init('dxs', len(dxdys))
    wire_patterns_capnp.init('dys', len(dxdys))

    for idx, dxdy in enumerate(dxdys):
        dxdy_to_dxdy_idx[dxdy] = idx
        wire_patterns_capnp.dxs[idx] = dxdy[0]
        wire_patterns_capnp.dys[idx] = dxdy[1]

    wire_patterns = []

    for wire_to_nodes, tile_pkeys in wire_to_node_patterns.items():
        wire_pattern = {}

        wires = []
        dxdys = []
        nodes = []

        for wire_in_tile_pkey, dx, dy, node_wire_in_tile_pkey in sorted(
                wire_to_nodes, key=lambda x: x.wire_in_tile_pkey):

            if dx == 0 and dy == 0 and wire_in_tile_pkey == node_wire_in_tile_pkey:
                continue

            assert wire_in_tile_pkey not in wire_pattern

            wires.append(wire_in_tile_pkey)
            dxdys.append(dxdy_to_dxdy_idx[(dx, dy)])
            nodes.append(node_wire_in_tile_pkey)

        wire_patterns.append(
            {
                'wires': wires,
                'dxdy_idxs': dxdys,
                'nodes': nodes,
                'tiles': sorted(tile_pkeys),
            })

    wire_patterns_capnp.init('wirePatterns', len(wire_patterns))
    for wire_pattern_out, wire_pattern in zip(wire_patterns_capnp.wirePatterns,
                                              wire_patterns):
        wire_pattern_out.init('dxdyIdxs', len(wire_pattern['dxdy_idxs']))
        wire_pattern_out.init('wires', len(wire_pattern['wires']))
        wire_pattern_out.init('nodes', len(wire_pattern['nodes']))
        wire_pattern_out.init('tiles', len(wire_pattern['tiles']))

    with open(args.wire_patterns, 'wb') as f:
        wire_patterns_capnp.write(f)

    node_patterns = []

    for tile_nodes_to_wire_pattern, tile_pkeys in tile_nodes_to_wire_patterns.items(
    ):
        node_pattern = {}
        for node_wire_in_tile_pkey, node_to_wires in tile_nodes_to_wire_pattern:

            assert node_wire_in_tile_pkey not in node_pattern

            dxs = []
            dys = []
            wires = []
            wire_pattern = []
            for wire_in_tile_pkey, dx, dy in sorted(node_to_wires):
                if dx == 0 and dy == 0 and wire_in_tile_pkey == node_wire_in_tile_pkey:
                    continue

                dxs.append(dx)
                dys.append(dy)
                wires.append(wire_in_tile_pkey)

            if dxs:
                node_pattern[node_wire_in_tile_pkey] = {
                    'dxs': dxs,
                    'dys': dys,
                    'wires': wires,
                }

        node_patterns.append(
            {
                'patterns': node_pattern,
                'tiles': sorted(tile_pkeys),
            })

    with open('node_patterns.json', 'w') as f:
        json.dump(node_patterns, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
