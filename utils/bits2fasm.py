#!/usr/bin/env python3
'''
Take raw .bits files and decode them to FASM.
'''

import os
import fasm
from prjxray import db
from prjxray import fasm_disassembler
from prjxray import bitstream


def run(db_root, bits_file, verbose, canonical):
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
        description='Convert 7-series bits file to FASM.')

    database_dir = os.getenv("XRAY_DATABASE_DIR")
    database = os.getenv("XRAY_DATABASE")
    db_root_kwargs = {}
    if database_dir is None or database is None:
        db_root_kwargs['required'] = True
    else:
        db_root_kwargs['required'] = False
        db_root_kwargs['default'] = os.path.join(database_dir, database)

    parser.add_argument('--db-root', help="Database root.", **db_root_kwargs)
    parser.add_argument('bits_file', help='')
    parser.add_argument(
        '--verbose',
        help='Print lines for unknown tiles and bits',
        action='store_true')
    parser.add_argument(
        '--canonical', help='Output canonical bitstream.', action='store_true')
    args = parser.parse_args()

    run(args.db_root, args.bits_file, args.verbose, args.canonical)


if __name__ == '__main__':
    main()
