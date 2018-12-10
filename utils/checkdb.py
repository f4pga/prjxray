#!/usr/bin/env python3
'''
Check:
-Individual files are valid
-No overlap between any tile

TODO:
Can we use prjxray?
Relies on 074, which is too far into the process
'''

from prjxray import util
from prjxray import db as prjxraydb
import os
import parsedb
#from prjxray import db as prjxraydb
import glob


def make_tile_mask(db_root, tile_name, tilej, strict=False, verbose=False):
    '''
    Return dict
    key: (address, bit index)
    val: sample description of where it came from (there may be multiple, only one)
    '''

    # FIXME: fix mask files https://github.com/SymbiFlow/prjxray/issues/301
    # in the meantime build them on the fly
    # We may want this to build them anyway

    ret = dict()
    for absaddr, bitaddr, tag in util.gen_tile_bits(
            db_root, tilej, strict=strict, verbose=verbose):
        name = "%s.%s" % (tile_name, tag)
        ret.setdefault((absaddr, bitaddr), name)
    return ret


def parsedb_all(db_root, verbose=False):
    '''Verify .db files are individually valid'''

    files = 0
    for bit_fn in glob.glob('%s/segbits_*.db' % db_root):
        verbose and print("Checking %s" % bit_fn)
        parsedb.run(bit_fn, fnout=None, strict=True, verbose=verbose)
        files += 1
    print("segbits_*.db: %d okay" % files)

    files = 0
    for bit_fn in glob.glob('%s/mask_*.db' % db_root):
        verbose and print("Checking %s" % bit_fn)
        parsedb.run(bit_fn, fnout=None, strict=True, verbose=verbose)
        files += 1
    print("mask_*.db: %d okay" % files)


def check_tile_overlap(db, db_root, strict=False, verbose=False):
    '''
    Verifies that no two tiles use the same bit

    Assume .db files are individually valid
    Create a mask for all the bits the tile type uses
    For each tile, create bitmasks over the entire bitstream for current part
    Throw an exception if two tiles share an address
    '''
    mall = dict()

    tiles_checked = 0
    for tile_name, tilej in db.tilegrid.items():
        #for tile_name, tilej in [("CLBLL_L_X12Y138", db.tilegrid["CLBLL_L_X12Y138"])]:
        mtile = make_tile_mask(
            db_root, tile_name, tilej, strict=strict, verbose=verbose)
        verbose and print(
            "Checking %s, type %s, bits: %s" %
            (tile_name, tilej["type"], len(mtile)))
        if len(mtile) == 0:
            continue

        collisions = set(mall.keys()).intersection(set(mtile.keys()))
        if collisions:
            print("ERROR: %s collisions" % len(collisions))
            for ck in sorted(collisions):
                addr, bitaddr = ck
                print(
                    "  %08X_%04X: had %s, got %s" %
                    (addr, bitaddr, mall[ck], mtile[ck]))
            raise ValueError("%s collisions" % len(collisions))
        mall.update(mtile)
        tiles_checked += 1
    print("Checked %s tiles, %s bits" % (tiles_checked, len(mall)))


def run(db_root, strict=False, verbose=False):
    # Start by running a basic check on db files
    print("Checking individual .db...")
    parsedb_all(db_root, verbose=verbose)

    # Now load and verify tile consistency
    db = prjxraydb.Database(db_root)
    db._read_tilegrid()
    '''
    these don't load properly without .json files
    See: https://github.com/SymbiFlow/prjxray/issues/303
    db._read_tile_types()
    print(db.tile_types.keys())
    '''

    verbose and print("")

    print("Checking aggregate dir...")
    check_tile_overlap(db, db_root, strict=strict, verbose=verbose)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Parse a db repository, checking for consistency")

    util.db_root_arg(parser)
    parser.add_argument('--strict', action='store_true', help='')
    parser.add_argument('--verbose', action='store_true', help='')
    args = parser.parse_args()

    run(args.db_root, strict=args.strict, verbose=args.verbose)


if __name__ == '__main__':
    main()
