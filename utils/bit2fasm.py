#!/usr/bin/env python3
'''
Take bitstream .bit files and decode them to FASM.
'''

import os
import fasm
from prjxray import db
from prjxray import fasm_disassembler
from prjxray import bitstream
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


def bits_to_fasm(db_root, bits_file, verbose, canonical):
    disassembler = fasm_disassembler.FasmDisassembler(db.Database(db_root))

    with open(bits_file) as f:
        bitdata = bitstream.load_bitdata(f)

    print(
        fasm.fasm_tuple_to_string(
            disassembler.find_features_in_bitstream(bitdata, verbose=verbose),
            canonical=canonical))


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
        '--part', help="Name of part being targetted.", **part_kwargs)
    parser.add_argument(
        '--bitread',
        help="Name of part being targetted.",
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

    with tempfile.NamedTemporaryFile() as bits_file:
        bit_to_bits(
            bitread=args.bitread,
            part_yaml=os.path.join(args.db_root, '{}.yaml'.format(args.part)),
            bit_file=args.bit_file,
            bits_file=bits_file.name,
            frame_range=args.frame_range,
        )

        bits_to_fasm(
            args.db_root, bits_file.name, args.verbose, args.canonical)


if __name__ == '__main__':
    main()
