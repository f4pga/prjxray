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
""" Tool for generating Vivavo commands to highlight objects from a FASM file.

Currently this tool only highlights pips directly referenced in the FASM file.
"""

from __future__ import print_function
import os.path
import fasm
from prjxray import db
from prjxray import util


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Outputs a Vivavo highlight_objects command from a FASM file.')

    util.db_root_arg(parser)
    util.part_arg(parser)
    parser.add_argument('fn_in', help='Input FPGA assembly (.fasm) file')

    args = parser.parse_args()
    database = db.Database(args.db_root, args.part)
    grid = database.grid()

    def inner():
        for line in fasm.parse_fasm_filename(args.fn_in):
            if not line.set_feature:
                continue

            parts = line.set_feature.feature.split('.')
            tile = parts[0]
            gridinfo = grid.gridinfo_at_tilename(tile)

            tile_type = database.get_tile_type(gridinfo.tile_type)

            for pip in tile_type.pips:
                if pip.net_from == parts[2] and pip.net_to == parts[1]:
                    yield '{}/{}'.format(tile, pip.name)

    print(
        'highlight_objects [concat {}]'.format(
            ' '.join('[get_pips {}]'.format(pip) for pip in inner())))


if __name__ == '__main__':
    main()
