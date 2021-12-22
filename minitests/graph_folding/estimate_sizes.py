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

import argparse

from prjxray import util
from prjxray.db import Database
import struct


def main():
    parser = argparse.ArgumentParser()
    util.db_root_arg(parser)
    util.part_arg(parser)

    args = parser.parse_args()

    db = Database(args.db_root, args.part)
    print('Reporting tile usage for part {}'.format(args.part))
    grid = db.grid()

    sizeof_delta = struct.calcsize('i')
    sizeof_wire_in_tile_idx = struct.calcsize('i')
    cost_per_wire = 2 * sizeof_delta + sizeof_wire_in_tile_idx
    max_wires_per_tile = 0
    _ = cost_per_wire

    all_wires = 0
    tile_type_to_count = {}
    for tile in grid.tiles():
        gridinfo = grid.gridinfo_at_tilename(tile)
        tile_type = gridinfo.tile_type

        if tile_type not in tile_type_to_count:
            tile_type_to_count[tile_type] = 0

        tile_type_to_count[tile_type] += 1

    tile_type_to_wires = {}
    for tile_type in tile_type_to_count:
        tile_type_info = db.get_tile_type(tile_type)
        tile_type_to_wires[tile_type] = len(tile_type_info.get_wires())
        all_wires += len(tile_type_info.get_wires())
        max_wires_per_tile = max(
            max_wires_per_tile, len(tile_type_info.get_wires()))

    for tile_type in sorted(
            tile_type_to_count, key=
            lambda tile_type: tile_type_to_count[tile_type] * tile_type_to_wires[tile_type]
    ):
        print(
            tile_type, tile_type_to_count[tile_type],
            tile_type_to_wires[tile_type])

    print('Total number of wires:', all_wires)
    print('Max wires per tile:', max_wires_per_tile)


if __name__ == "__main__":
    main()
