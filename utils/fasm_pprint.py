#!/usr/bin/env python3
'''
Pretty print FASM.

Sanity checks FASM against prjxray database.
Can output canonical FASM.
In the future may support other formatting options.

'''

import os
import fasm
from prjxray import db


def process_fasm(db_root, fasm_file, canonical):
    database = db.Database(db_root)
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


def run(db_root, fasm_file, canonical):
    print(
        fasm.fasm_tuple_to_string(
            process_fasm(db_root, fasm_file, canonical), canonical=canonical))


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Pretty print a FASM file.')

    database_dir = os.getenv("XRAY_DATABASE_DIR")
    database = os.getenv("XRAY_DATABASE")
    db_root_kwargs = {}
    if database_dir is None or database is None:
        db_root_kwargs['required'] = True
    else:
        db_root_kwargs['required'] = False
        db_root_kwargs['default'] = os.path.join(database_dir, database)

    parser.add_argument('--db-root', help="Database root.", **db_root_kwargs)
    parser.add_argument('fasm_file', help='Input FASM file')
    parser.add_argument(
        '--canonical', help='Output canonical bitstream.', action='store_true')
    args = parser.parse_args()

    run(args.db_root, args.fasm_file, args.canonical)


if __name__ == '__main__':
    main()
