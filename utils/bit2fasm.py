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
Take bitstream .bit files and decode them to FASM.
'''

import contextlib
import os
import fasm
import fasm.output
from prjxray import fasm_disassembler
from prjxray import bitstream
from prjxray.db import Database
from prjxray.util import OpenSafeFile
import subprocess
import tempfile


def bit_to_bits(bitread, part_yaml, bit_file, bits_file, frame_range=None):
    """ Calls bitread to create bits (ASCII) from bit file (binary) """
    if frame_range:
        frame_range_arg = '-F {}'.format(frame_range)
    else:
        frame_range_arg = ''

    subprocess.check_output(
        '{} --part_file {} {} -o {} -z -y {}'.format(
            bitread, part_yaml, frame_range_arg, bits_file, bit_file),
        shell=True)


def bits_to_fasm(db_root, part, bits_file, verbose, canonical):
    db = Database(db_root, part)
    grid = db.grid()
    disassembler = fasm_disassembler.FasmDisassembler(db)

    with OpenSafeFile(bits_file) as f:
        bitdata = bitstream.load_bitdata(f)

    model = fasm.output.merge_and_sort(
        disassembler.find_features_in_bitstream(bitdata, verbose=verbose),
        zero_function=disassembler.is_zero_feature,
        sort_key=grid.tile_key,
    )

    print(fasm.fasm_tuple_to_string(model, canonical=canonical), end='')


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Convert 7-series bit file to FASM.')

    database_dir = os.getenv("XRAY_DATABASE_DIR")
    database = os.getenv("XRAY_DATABASE")
    db_root_kwargs = {}
    if database_dir is None or database is None:
        db_root_kwargs['required'] = True
    else:
        db_root_kwargs['required'] = False
        db_root_kwargs['default'] = os.path.join(database_dir, database)

    default_part = os.getenv("XRAY_PART")
    part_kwargs = {}
    if default_part is None:
        part_kwargs['required'] = True
    else:
        part_kwargs['required'] = False
        part_kwargs['default'] = default_part

    if os.getenv("XRAY_TOOLS_DIR") is None:
        default_bitread = 'bitread'
    else:
        default_bitread = os.path.join(os.getenv("XRAY_TOOLS_DIR"), 'bitread')

    parser.add_argument('--db-root', help="Database root.", **db_root_kwargs)
    parser.add_argument(
        '--bits-file',
        help="Output filename for bitread output, default is deleted tempfile.",
        default=None)
    parser.add_argument(
        '--part', help="Name of part being targetted.", **part_kwargs)
    parser.add_argument(
        '--bitread',
        help="bitread tool to to use",
        default=default_bitread)
    parser.add_argument(
        '--frame_range', help="Frame range to use with bitread.")
    parser.add_argument('bit_file', help='')
    parser.add_argument(
        '--verbose',
        help='Print lines for unknown tiles and bits',
        action='store_true')
    parser.add_argument(
        '--canonical', help='Output canonical bitstream.', action='store_true')
    args = parser.parse_args()

    with contextlib.ExitStack() as stack:
        if args.bits_file:
            bits_file = stack.enter_context(open(args.bits_file, 'wb'))
        else:
            bits_file = stack.enter_context(tempfile.NamedTemporaryFile())

        bit_to_bits(
            bitread=args.bitread,
            part_yaml=os.path.join(args.db_root, args.part, "part.yaml"),
            bit_file=args.bit_file,
            bits_file=bits_file.name,
            frame_range=args.frame_range,
        )

        bits_to_fasm(
            args.db_root, args.part, bits_file.name, args.verbose,
            args.canonical)


if __name__ == '__main__':
    main()
