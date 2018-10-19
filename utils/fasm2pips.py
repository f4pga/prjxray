#!/usr/bin/env python3

from __future__ import print_function
import os.path
import fasm
from prjxray import db


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Convert FASM to pip list')

    database_dir = os.getenv("XRAY_DATABASE_DIR")
    database = os.getenv("XRAY_DATABASE")
    db_root_kwargs = {}
    if database_dir is None or database is None:
        db_root_kwargs['required'] = True
    else:
        db_root_kwargs['required'] = False
        db_root_kwargs['default'] = os.path.join(database_dir, database)

    parser.add_argument('--db_root', help="Database root.", **db_root_kwargs)
    parser.add_argument('fn_in', help='Input FPGA assembly (.fasm) file')

    args = parser.parse_args()
    database = db.Database(args.db_root)
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
                    yield '{}/{}.{}'.format(tile, gridinfo.tile_type, pip.name)

    print(
        'highlight_objects [concat {}]'.format(
            ' '.join('[get_pips {}]'.format(pip) for pip in inner())))


if __name__ == '__main__':
    main()
