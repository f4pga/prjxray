#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

import sys, os, json
import pickle

from prjxray.util import OpenSafeFile

class MergeFind:
    def __init__(self):
        self.db = dict()

    def merge(self, a, b):
        a = self.find(a)
        b = self.find(b)
        if a != b:
            self.db[a] = b

    def find(self, a):
        if a in self.db:
            c = self.find(self.db[a])
            self.db[a] = c
            return c
        return a


def db_gen():
    print("Reading database..")

    with OpenSafeFile("%s/%s/tilegrid.json" % (os.getenv("XRAY_DATABASE_DIR"),
                                       os.getenv("XRAY_DATABASE")), "r") as f:
        tilegrid = json.load(f)

    with OpenSafeFile("%s/%s/tileconn.json" % (os.getenv("XRAY_DATABASE_DIR"),
                                       os.getenv("XRAY_DATABASE")), "r") as f:
        tileconn = json.load(f)

    type_to_tiles = dict()
    grid_to_tile = dict()
    nodes = MergeFind()

    for tile, tiledata in tilegrid.items():
        if tiledata["type"] not in type_to_tiles:
            type_to_tiles[tiledata["type"]] = list()
        type_to_tiles[tiledata["type"]].append(tile)
        grid_to_tile[(tiledata["grid_x"], tiledata["grid_y"])] = tile

    print("Processing tileconn..")

    for entry in tileconn:
        type_a, type_b = entry["tile_types"]
        for tile_a in type_to_tiles[type_a]:
            tiledata_a = tilegrid[tile_a]
            grid_a = (tiledata_a["grid_x"], tiledata_a["grid_y"])
            grid_b = (
                grid_a[0] + entry["grid_deltas"][0],
                grid_a[1] + entry["grid_deltas"][1])

            if grid_b not in grid_to_tile:
                continue

            tile_b = grid_to_tile[grid_b]
            tiledata_b = tilegrid[tile_b]

            if tiledata_b["type"] != type_b:
                continue

            for pair in entry["wire_pairs"]:
                nodes.merge((tile_a, pair[0]), (tile_b, pair[1]))

    print("Processing PIPs..")

    node_node_pip = dict()
    reverse_node_node = dict()

    for tile_type in ["int_l", "int_r"]:
        with OpenSafeFile("%s/%s/segbits_%s.db" %
                  (os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"),
                   tile_type), "r") as f:
            for line in f:
                _, dst, src = line.split()[0].split(".")
                for tile in type_to_tiles[tile_type.upper()]:
                    src_node = nodes.find((tile, src))
                    dst_node = nodes.find((tile, dst))
                    if src_node not in node_node_pip:
                        node_node_pip[src_node] = dict()
                    if dst_node not in reverse_node_node:
                        reverse_node_node[dst_node] = set()
                    node_node_pip[src_node][dst_node] = "%s.%s.%s" % (
                        tile, dst, src)
                    reverse_node_node[dst_node].add(src_node)

    return type_to_tiles, grid_to_tile, nodes, node_node_pip, reverse_node_node


def db_load():
    # Takes a while. Speed things up
    picklef = os.getenv('XRAY_DIR') + '/tools/simpleroute.p'
    if os.path.exists(picklef):
        #print('Pickle: load')
        db_res = pickle.load(open(picklef, 'rb'))
    else:
        #print('Pickle: rebuilding')
        db_res = db_gen()
        #print('Pickle: save')
        pickle.dump(db_res, open(picklef, 'wb'))
    return db_res


def route(args):
    type_to_tiles, grid_to_tile, nodes, node_node_pip, reverse_node_node = db_load(
    )

    active_pips = set()
    blocked_nodes = set()

    for argidx in range((len(args)) // 2):
        src_tile, src_wire = args[2 * argidx].split("/")
        dst_tile, dst_wire = args[2 * argidx + 1].split("/")

        src_node = nodes.find((src_tile, src_wire))
        dst_node = nodes.find((dst_tile, dst_wire))

        print("Routing %s -> %s:" % (src_node, dst_node))

        node_scores = dict()

        def write_scores(nodes, count):
            next_nodes = set()
            for n in nodes:
                if n in node_scores:
                    continue
                node_scores[n] = count
                if n == src_node:
                    return
                if n in reverse_node_node:
                    for nn in reverse_node_node[n]:
                        if nn not in node_scores and nn not in blocked_nodes:
                            next_nodes.add(nn)
            write_scores(next_nodes, count + 1)

        try:
            write_scores(set([dst_node]), 1)
        except RecursionError as e:
            raise Exception(
                "Could not find route for node %s" % (dst_node, )) from None
        print("  route length: %d" % node_scores[src_node])

        count = 0
        c = src_node
        blocked_nodes.add(c)
        print("  %4d: %s" % (count, c))

        score = node_scores[src_node]
        while c != dst_node:
            nn = None
            for n in node_node_pip[c].keys():
                if n in node_scores and node_scores[n] < score:
                    nn, score = n, node_scores[n]

            pip = node_node_pip[c][nn]
            active_pips.add(pip)
            print("        %s" % pip)

            count += 1
            c = nn
            blocked_nodes.add(c)
            print("  %4d: %s" % (count, c))

    print("====")
    pipnames = list()

    for pip in sorted(active_pips):
        tile, dst, src = pip.split(".")
        pipnames.append("%s/%s.%s->>%s" % (tile, tile[0:5], src, dst))

    print(
        "highlight_objects -color orange [get_nodes -of_objects [get_wires {%s}]]"
        % " ".join(["%s/%s" % n for n in sorted(blocked_nodes)]))
    print(
        "highlight_objects -color orange [get_pips {%s}]" % " ".join(pipnames))

    print("====")
    for pip in sorted(active_pips):
        print(pip)
    return active_pips


if __name__ == '__main__':
    if len(sys.argv) == 1 or (len(sys.argv) % 2) != 1:
        print()
        print("Usage: %s src1 dst1 [src2 dst2 [...]]" % sys.argv[0])
        print("Where entires as tile/wire")
        print()
        print(
            "Example: %s VBRK_X29Y140/VBRK_ER1BEG2 VFRAME_X47Y113/VFRAME_EL1BEG2"
            % sys.argv[0])
        print()
        sys.exit(1)
    route(sys.argv[1:])
