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
#
# Produces a complete database of wires in the ROI and their connections and tests if each
# routing node is a tree (i.e. fails with an error when a loop is found).

import os, sys, json

from prjxray.util import OpenSafeFile

def main():
    with OpenSafeFile("%s/%s/tilegrid.json" % (os.getenv("XRAY_DATABASE_DIR"),
                                       os.getenv("XRAY_DATABASE")), "r") as f:
        tilegrid = json.load(f)

    with OpenSafeFile("%s/%s/tileconn.json" % (os.getenv("XRAY_DATABASE_DIR"),
                                       os.getenv("XRAY_DATABASE")), "r") as f:
        tileconn = json.load(f)

    grid = dict()
    wirepairs = dict()
    remwires = set()

    for tilename, tiledata in tilegrid.items():
        key = (tiledata["grid_x"], tiledata["grid_y"])
        grid[key] = tilename

    def check_tileconn_entry(tilename, tiledata, entry, idx):
        if idx == 0:
            otheridx = 1
            otherxy = (
                tiledata["grid_x"] + entry["grid_deltas"][0],
                tiledata["grid_y"] + entry["grid_deltas"][1])
        else:
            otheridx = 0
            otherxy = (
                tiledata["grid_x"] - entry["grid_deltas"][0],
                tiledata["grid_y"] - entry["grid_deltas"][1])

        if otherxy not in grid:
            return

        othertilename = grid[otherxy]
        othertiledata = tilegrid[othertilename]

        if othertiledata["type"] != entry["tile_types"][otheridx]:
            return

        print(
            "  Found relevant entry (%s %s %d %d): %s" % (
                entry["tile_types"][0], entry["tile_types"][1],
                entry["grid_deltas"][0], entry["grid_deltas"][1],
                othertilename))

        for pair in entry["wire_pairs"]:
            wirename = "%s/%s" % (tilename, pair[idx])
            otherwirename = "%s/%s" % (othertilename, pair[otheridx])

            remwires.add(wirename)
            remwires.add(otherwirename)

            if wirename not in wirepairs:
                wirepairs[wirename] = set()
            wirepairs[wirename].add(otherwirename)

            if otherwirename not in wirepairs:
                wirepairs[otherwirename] = set()
            wirepairs[otherwirename].add(wirename)

    for tilename, tiledata in tilegrid.items():
        print("Connecting wires in tile %s." % tilename)
        for entry in tileconn:
            if entry["tile_types"][0] == tiledata["type"]:
                check_tileconn_entry(tilename, tiledata, entry, 0)
            if entry["tile_types"][1] == tiledata["type"]:
                check_tileconn_entry(tilename, tiledata, entry, 1)

    def check_wire(wire, source):
        for next_wire in wirepairs[wire]:
            if next_wire == source:
                continue
            print("  %s" % next_wire)
            if next_wire not in remwires:
                print("  ** FOUND LOOP IN THIS NODE **")
                sys.exit(1)
            remwires.remove(next_wire)
            check_wire(next_wire, wire)

    while len(remwires):
        wire = remwires.pop()
        print("Checking %s:" % wire)
        check_wire(wire, None)

    print("NO LOOP FOUND: OK")


if __name__ == "__main__":
    main()
