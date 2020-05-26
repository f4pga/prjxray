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
'''
Pretty print FASM.

Sanity checks FASM against prjxray database.
Can output canonical FASM.
In the future may support other formatting options.

'''

import os
import fasm
from prjxray import db


def process_fasm(db_root, part, fasm_file, canonical):
    database = db.Database(db_root, part)
    grid = database.grid()

    for fasm_line in fasm.parse_fasm_filename(fasm_file):
        if not fasm_line.set_feature:
            if not canonical:
                yield fasm_line

        for feature in fasm.canonical_features(fasm_line.set_feature):
            parts = feature.feature.split('.')
            tile = parts[0]

            gridinfo = grid.gridinfo_at_tilename(tile)
            tile_segbits = database.get_tile_segbits(gridinfo.tile_type)

            address = 0
            if feature.start is not None:
                address = feature.start

            feature_name = '{}.{}'.format(
                gridinfo.tile_type, '.'.join(parts[1:]))

            # Convert feature to bits.  If no bits are set, feature is
            # psuedo pip, and should not be output from canonical FASM.
            bits = tuple(
                tile_segbits.feature_to_bits(feature_name, address=address))
            if len(bits) == 0 and canonical:
                continue

            # In canonical output, only output the canonical features.
            if canonical:
                yield fasm.FasmLine(
                    set_feature=feature,
                    annotations=None,
                    comment=None,
                )

        # If not in canonical mode, output original FASM line
        if not canonical:
            yield fasm_line


def run(db_root, part, fasm_file, canonical):
    print(
        fasm.fasm_tuple_to_string(
            process_fasm(db_root, part, fasm_file, canonical),
            canonical=canonical))


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Pretty print a FASM file.')

    util.db_root_arg(parser)
    util.part_arg(parser)
    parser.add_argument('fasm_file', help='Input FASM file')
    parser.add_argument(
        '--canonical', help='Output canonical bitstream.', action='store_true')
    args = parser.parse_args()

    run(args.db_root, args.part, args.fasm_file, args.canonical)


if __name__ == '__main__':
    main()
