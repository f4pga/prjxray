#!/usr/bin/env python3

'''
Check:
-Individual files are valid
-No overlap between any tile
'''

import sys, re
from prjxray import util
import parsedb
#from prjxray import db as prjxraydb
import glob


def parsedb_all(db_root, verbose=False):
    '''Verify .db files are individually valid'''

    for bit_fn in glob.glob('%s/segbits_*.db'):
        parsedb.run(bit_fn, fnout=None, strict=True, verbose=verbose)

    for bit_fn in glob.glob('%s/mask_*.db'):
        parsedb.run(bit_fn, fnout=None, strict=True, verbose=verbose)

def process_db(tile_type, process, verbose):
    #ttdb = db.get_tile_type(tile_type)

    fns = [ttdb.tile_dbs.segbits, ttdb.tile_dbs.ppips]
    verbose and print("process_db(%s): %s" % (tile_type, fns))
    for fn in fns:
        if fn:
            with open(fn, "r") as f:
                for line in f:
                    process(util.parse_db_line(line))


def check_seg_overlap(db_root, verbose=False):
    '''
    Assume .db files are individually valid
    Create a mask for all the bits the tile type uses
    For each tile, create bitmasks over the entire bitstream for current part
    Throw an exception if two tiles share an address
    '''
    # key: (address, bit index)
    # val: sample description of where it came from (there may be multiple, only one)
    used = dict()

    tiles_checked = 0
    for tile_name, tile in db.tilegrid.items():
        #ttdb = db.get_tile_type(tile["type"])
        # FIXME: check BRAM
        bitj = tile["bits"].get("CLB_IO_CLK", None)
        if not bitj:
            continue
        verbose and print("Checking %s, type %s" % (tile_name, tile["type"]))
        baseaddr = int(bitj["baseaddr"], 0)
        bitbase = 32 * bitj["offset"]

        # Create tile mask
        tile_used = dict()
        def process(lparse):
            tag, bits, mode = lparse
            assert mode is None
            for (bit_addroff, bit_bitoff) in bits:
                tile_used[(baseaddr + bit_addroff, bitbase + bit_bitoff)] = "%s.%s" % (tile_name, tag)
        process_db(tile["type"], process, verbose=verbose)

        # See if tile mask intersects any existing bits
        for (waddr, bitaddr), tile_desc in tile_used.items():
            used_desc = used.get((waddr, bitaddr), None)
            if used_desc:
                raise ValueError("Collision at %08X:%04X: had %s, got %s" % (waddr, bitaddr, used_desc, tile_desc))
            used[(waddr, bitaddr)] = tile_desc
        tiles_checked += 1
    print("Checked %s tiles, %s bits" % tiles_checked, len(used))


def run(db_root, verbose=False):
    # Start by running a basic check on db files
    parsedb_all(db_root, verbose=verbose)

    '''
    # Now load and verify tile consistency
    db = prjxraydb.Database(db_root)
    db._read_tilegrid()
    db._read_tile_types()
    print(db.tile_types.keys())
    '''

    check_seg_overlap(db_root, verbose=verbose)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Parse a db repository, checking for consistency")

    util.db_root_arg(parser)
    parser.add_argument('--verbose', action='store_true', help='')
    args = parser.parse_args()

    run(args.db_root, verbose=args.verbose)


if __name__ == '__main__':
    main()
