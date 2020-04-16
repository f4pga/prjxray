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
import utils.parsedb as parsedb
#from prjxray import db as prjxraydb
import glob


def gen_tile_bits(tile_segbits, tile_bits):
    '''
    For given tile and corresponding db_file structure yield
    (absolute address, absolute FDRI bit offset, tag)

    For each tag bit in the corresponding block_type entry, calculate absolute address and bit offsets
    '''

    for block_type in tile_segbits:
        assert block_type in tile_bits, "block type %s is not present in current tile" % block_type

        block = tile_bits[block_type]

        baseaddr = block.base_address
        bitbase = 32 * block.offset
        frames = block.frames

        for tag in tile_segbits[block_type]:
            for bit in tile_segbits[block_type][tag]:
                # 31_06
                word_column = bit.word_column
                word_bit = bit.word_bit
                assert word_column <= frames, "ERROR: bit out of bound --> tag: %s; word_column = %s; frames = %s" % (
                    tag, word_column, frames)
                yield word_column + baseaddr, word_bit + bitbase, tag


def make_tile_mask(tile_segbits, tile_name, tile_bits):
    '''
    Return dict
    key: (address, bit index)
    val: sample description of where it came from (there may be multiple, only one)
    '''

    # FIXME: fix mask files https://github.com/SymbiFlow/prjxray/issues/301
    # in the meantime build them on the fly
    # We may want this to build them anyway

    ret = dict()
    for absaddr, bitaddr, tag in gen_tile_bits(tile_segbits, tile_bits):
        name = "%s.%s" % (tile_name, tag)
        ret.setdefault((absaddr, bitaddr), name)
    return ret


def parsedb_all(db_root, verbose=False):
    '''Verify .db files are individually valid'''

    files = 0
    for bit_fn in glob.glob('%s/segbits_*.db' % db_root):
        # Don't parse db files with fuzzer origin information
        if "origin_info" in bit_fn:
            continue
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


def check_tile_overlap(db, verbose=False):
    '''
    Verifies that no two tiles use the same bit

    Assume .db files are individually valid
    Create a mask for all the bits the tile type uses
    For each tile, create bitmasks over the entire bitstream for current part
    Throw an exception if two tiles share an address
    '''
    mall = dict()
    tiles_type_done = dict()
    tile_segbits = dict()
    grid = db.grid()
    tiles_checked = 0

    for tile_name in grid.tiles():
        tile_info = grid.gridinfo_at_tilename(tile_name)
        tile_type = tile_info.tile_type
        tile_bits = tile_info.bits

        if tile_type not in tiles_type_done:
            segbits = db.get_tile_segbits(tile_type).segbits
            tile_segbits[tile_type] = segbits

            # If segbits has zero length the tile_type is marked True in order to be skipped
            if len(segbits) == 0:
                tiles_type_done[tile_type] = True
            else:
                tiles_type_done[tile_type] = False

        if tiles_type_done[tile_type]:
            continue

        mtile = make_tile_mask(tile_segbits[tile_type], tile_name, tile_bits)
        verbose and print(
            "Checking %s, type %s, bits: %s" %
            (tile_name, tile_type, len(mtile)))
        if len(mtile) == 0:
            continue

        collisions = set()
        for bits in mtile.keys():
            if bits in mall.keys():
                collisions.add(bits)

        if collisions:
            print("ERROR: %s collisions" % len(collisions))
            for ck in sorted(collisions):
                addr, bitaddr = ck
                word, bit = util.addr_bit2word(bitaddr)
                print(
                    "  %s: had %s, got %s" %
                    (util.addr2str(addr, word, bit), mall[ck], mtile[ck]))
            raise ValueError("%s collisions" % len(collisions))
        mall.update(mtile)
        tiles_checked += 1
    print("Checked %s tiles, %s bits" % (tiles_checked, len(mall)))


def run(db_root, part, verbose=False):
    # Start by running a basic check on db files
    print("Checking individual .db...")
    parsedb_all(db_root, verbose=verbose)

    # Now load and verify tile consistency
    db = prjxraydb.Database(db_root, part)
    db._read_tilegrid()
    '''
    these don't load properly without .json files
    See: https://github.com/SymbiFlow/prjxray/issues/303
    db._read_tile_types()
    print(db.tile_types.keys())
    '''

    verbose and print("")

    print("Checking aggregate dir...")
    check_tile_overlap(db, verbose=verbose)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Parse a db repository, checking for consistency")

    util.db_root_arg(parser)
    util.part_arg(parser)
    parser.add_argument('--verbose', action='store_true', help='')
    args = parser.parse_args()

    run(args.db_root, args.part, verbose=args.verbose)


if __name__ == '__main__':
    main()
