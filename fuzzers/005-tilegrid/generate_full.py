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
import copy
import json
import os
from utils import xjson
'''
Historically we grouped data into "segments"
These were a region of the bitstream that encoded one or more tiles
However, this didn't scale with certain tiles like BRAM
Some sites had multiple bitstream areas and also occupied multiple tiles

Decoding was then shifted to instead describe how each title is encoded
A post processing step verifies that two tiles don't reference the same bitstream area
'''

import util as localutil


def nolr(tile_type):
    '''
    Remove _L or _R suffix tile_type suffix, if present
    Ex: BRAM_INT_INTERFACE_L => BRAM_INT_INTERFACE
    Ex: VBRK => VBRK
    '''
    postfix = tile_type[-2:]
    if postfix in ('_L', '_R'):
        return tile_type[:-2]
    else:
        return tile_type


def make_tiles_by_grid(database):
    # lookup tile names by (X, Y)
    tiles_by_grid = dict()

    for tile_name in database:
        tile = database[tile_name]
        tiles_by_grid[(tile["grid_x"], tile["grid_y"])] = tile_name

    return tiles_by_grid


def propagate_INT_lr_bits(
        database, tiles_by_grid, tile_frames_map, verbose=False):
    '''Populate segment base addresses: L/R along INT column'''

    int_frames, int_words, _ = localutil.get_entry('INT', 'CLB_IO_CLK')

    verbose and print('')
    for tile in database:
        if database[tile]["type"] not in ["INT_L", "INT_R"]:
            continue

        if not database[tile]["bits"]:
            continue

        grid_x = database[tile]["grid_x"]
        grid_y = database[tile]["grid_y"]
        baseaddr = int(database[tile]["bits"]["CLB_IO_CLK"]["baseaddr"], 0)
        offset = database[tile]["bits"]["CLB_IO_CLK"]["offset"]

        if database[tile]["type"] == "INT_L":
            grid_x += 1
            baseaddr = baseaddr + 0x80
        elif database[tile]["type"] == "INT_R":
            grid_x -= 1
            baseaddr = baseaddr - 0x80
        else:
            assert 0, database[tile]["type"]

        # ROI at edge?
        if (grid_x, grid_y) not in tiles_by_grid:
            verbose and print('  Skip edge')
            continue

        other_tile = tiles_by_grid[(grid_x, grid_y)]

        if database[tile]["type"] == "INT_L":
            assert database[other_tile]["type"] == "INT_R"
        elif database[tile]["type"] == "INT_R":
            assert database[other_tile]["type"] == "INT_L"
        else:
            assert 0

        localutil.add_tile_bits(
            other_tile, database[other_tile], baseaddr, offset, int_frames,
            int_words, tile_frames_map)


def propagate_INT_bits_in_column(database, tiles_by_grid, tile_frames_map):
    """ Propigate INT offsets up and down INT columns.

    INT columns appear to be fairly regular, where starting from offset 0,
    INT tiles next to INT tiles increase the word offset by 2.  The HCLK tile
    is surrounded above and sometimes below by an INT tile.  Because the HCLK
    tile only useds one word, the offset increase by one at the HCLK.

    """

    seen_int = set()

    int_frames, int_words, _ = localutil.get_entry('INT', 'CLB_IO_CLK')
    hclk_frames, hclk_words, _ = localutil.get_entry('HCLK', 'CLB_IO_CLK')

    for tile_name in sorted(database.keys()):
        tile = database[tile_name]

        if tile['type'] not in ['INT_L', 'INT_R']:
            continue

        l_or_r = tile['type'][-1]

        if not tile['bits']:
            continue

        if tile_name in seen_int:
            continue

        # Walk down INT column
        while True:
            seen_int.add(tile_name)

            next_tile = tiles_by_grid[(tile['grid_x'], tile['grid_y'] + 1)]
            next_tile_type = database[next_tile]['type']

            if tile['bits']['CLB_IO_CLK']['offset'] == 0:
                assert next_tile_type in [
                    'B_TERM_INT', 'BRKH_INT', 'BRKH_B_TERM_INT'
                ], next_tile_type
                break

            baseaddr = int(tile['bits']['CLB_IO_CLK']['baseaddr'], 0)
            offset = tile['bits']['CLB_IO_CLK']['offset']

            if tile['type'].startswith(
                    'INT_') and next_tile_type == tile['type']:
                # INT next to INT
                offset -= int_words
                localutil.add_tile_bits(
                    next_tile, database[next_tile], baseaddr, offset,
                    int_frames, int_words, tile_frames_map)
            elif tile['type'].startswith('INT_'):
                # INT above HCLK
                assert next_tile_type.startswith(
                    'HCLK_{}'.format(l_or_r)), next_tile_type

                offset -= hclk_words
                localutil.add_tile_bits(
                    next_tile, database[next_tile], baseaddr, offset,
                    hclk_frames, hclk_words, tile_frames_map)
            else:
                # HCLK above INT
                assert tile['type'].startswith(
                    'HCLK_{}'.format(l_or_r)), tile['type']
                if next_tile_type == 'INT_{}'.format(l_or_r):
                    offset -= int_words
                    localutil.add_tile_bits(
                        next_tile, database[next_tile], baseaddr, offset,
                        int_frames, int_words, tile_frames_map)
                else:
                    # Handle special case column where the PCIE tile is present.
                    assert next_tile_type in ['PCIE_NULL'], next_tile_type
                    break

            tile_name = next_tile
            tile = database[tile_name]

        # Walk up INT column
        while True:
            seen_int.add(tile_name)

            next_tile = tiles_by_grid[(tile['grid_x'], tile['grid_y'] - 1)]
            next_tile_type = database[next_tile]['type']

            if tile['bits']['CLB_IO_CLK']['offset'] == 99:
                assert next_tile_type in [
                    'T_TERM_INT', 'BRKH_INT', 'BRKH_TERM_INT', 'BRKH_INT_PSS'
                ], next_tile_type
                break

            baseaddr = int(tile['bits']['CLB_IO_CLK']['baseaddr'], 0)
            offset = tile['bits']['CLB_IO_CLK']['offset']

            if tile['type'].startswith(
                    'INT_') and next_tile_type == tile['type']:
                # INT next to INT
                offset += int_words
                localutil.add_tile_bits(
                    next_tile, database[next_tile], baseaddr, offset,
                    int_frames, int_words, tile_frames_map)
            elif tile['type'].startswith('INT_'):
                # INT below HCLK
                assert next_tile_type.startswith(
                    'HCLK_{}'.format(l_or_r)), next_tile_type

                offset += int_words
                localutil.add_tile_bits(
                    next_tile, database[next_tile], baseaddr, offset,
                    hclk_frames, hclk_words, tile_frames_map)
            else:
                # HCLK below INT
                assert tile['type'].startswith(
                    'HCLK_{}'.format(l_or_r)), tile['type']
                assert next_tile_type == 'INT_{}'.format(
                    l_or_r), next_tile_type

                offset += hclk_words
                localutil.add_tile_bits(
                    next_tile, database[next_tile], baseaddr, offset,
                    int_frames, int_words, tile_frames_map)

            tile_name = next_tile
            tile = database[tile_name]


def propagate_INT_INTERFACE_bits_in_column(
        database, tiles_by_grid, int_interface_name, tile_frames_map):
    """ Propagate INT_INTERFACE column for a given INT_INTERFACE tile name.

    INT_INTERFACE tiles do not usually have any PIPs or baseaddresses,
    except for a few cases such as PCIE or GTP INTERFACE tiles.

    These are very regular tiles, except for the horizontal clock line,
    which adds a one-word offset.

    This function replicates the baseaddress and calculates the correct offset
    for each INT INTERFACE tile in a column, starting from a tile in the column
    that has the baseaddress calculated from the corresponding tilegrid fuzzer.
    """

    seen_int = set()

    int_frames, int_words, _ = localutil.get_entry('INT', 'CLB_IO_CLK')
    hclk_frames, hclk_words, _ = localutil.get_entry('HCLK', 'CLB_IO_CLK')

    for tile_name in sorted(database.keys()):
        tile = database[tile_name]

        if not tile['type'].startswith(int_interface_name):
            continue

        if not tile['bits']:
            continue

        if tile_name in seen_int:
            continue

        # Walk down INT column
        down_tile = tile
        down_tile_name = tile_name
        while True:
            seen_int.add(down_tile_name)

            baseaddr = int(down_tile['bits']['CLB_IO_CLK']['baseaddr'], 0)
            offset = down_tile['bits']['CLB_IO_CLK']['offset']
            extra_offset = 0

            next_tile = tiles_by_grid[(
                down_tile['grid_x'], down_tile['grid_y'] + 1)]
            if next_tile.startswith("HCLK"):
                next_tile = tiles_by_grid[(
                    down_tile['grid_x'], down_tile['grid_y'] + 2)]
                extra_offset = hclk_words

            next_tile_type = database[next_tile]['type']

            if next_tile_type != tile['type']:
                break

            if next_tile_type == down_tile['type']:
                # INT next to INT
                offset -= (int_words + extra_offset)
                localutil.add_tile_bits(
                    next_tile, database[next_tile], baseaddr, offset,
                    int_frames, int_words, tile_frames_map)

            down_tile_name = next_tile
            down_tile = database[down_tile_name]

        # Walk up INT column
        up_tile = tile
        up_tile_name = tile_name
        while True:
            seen_int.add(up_tile_name)

            baseaddr = int(up_tile['bits']['CLB_IO_CLK']['baseaddr'], 0)
            offset = up_tile['bits']['CLB_IO_CLK']['offset']
            extra_offset = 0

            next_tile = tiles_by_grid[(
                up_tile['grid_x'], up_tile['grid_y'] - 1)]
            if next_tile.startswith("HCLK"):
                next_tile = tiles_by_grid[(
                    up_tile['grid_x'], up_tile['grid_y'] - 2)]
                extra_offset = hclk_words

            next_tile_type = database[next_tile]['type']

            if next_tile_type != tile['type']:
                break

            if next_tile_type == up_tile['type']:
                # INT next to INT
                offset += (int_words + extra_offset)
                localutil.add_tile_bits(
                    next_tile, database[next_tile], baseaddr, offset,
                    int_frames, int_words, tile_frames_map)

            up_tile_name = next_tile
            up_tile = database[up_tile_name]


def propagate_rebuf(database, tiles_by_grid):
    """ Writing a fuzzer for the CLK_BUFG_REBUF tiles is hard, so propigate from CLK_HROW tiles.

    In the clock column, there is a CLK_BUFG_REBUF above and below the CLK_HROW
    tile.  Each clock column appears to use the same offsets, so propigate
    the base address and frame count, and update the offset and word count.

    """
    for tile_name in sorted(database.keys()):
        tile = database[tile_name]

        if tile['type'] not in ['CLK_HROW_BOT_R', 'CLK_HROW_TOP_R']:
            continue

        rebuf_below = tiles_by_grid[(tile['grid_x'], tile['grid_y'] - 12)]
        assert database[rebuf_below]['type'] == 'CLK_BUFG_REBUF', database[
            rebuf_below]['type']
        rebuf_above = tiles_by_grid[(tile['grid_x'], tile['grid_y'] + 13)]
        assert database[rebuf_above]['type'] == 'CLK_BUFG_REBUF', database[
            rebuf_below]['type']

        assert database[tile_name]['bits']['CLB_IO_CLK'][
            'offset'] == 42, database[tile_name]['bits']['CLB_IO_CLK']
        database[rebuf_below]['bits'] = copy.deepcopy(
            database[tile_name]['bits'])
        database[rebuf_below]['bits']['CLB_IO_CLK']['offset'] = 73
        database[rebuf_below]['bits']['CLB_IO_CLK']['words'] = 4

        database[rebuf_above]['bits'] = copy.deepcopy(
            database[tile_name]['bits'])
        database[rebuf_above]['bits']['CLB_IO_CLK']['offset'] = 24
        database[rebuf_above]['bits']['CLB_IO_CLK']['words'] = 4


def propagate_IOB_SING(database, tiles_by_grid):
    """ The IOB_SING are half tiles at top and bottom of every IO column.

    Unlike most tiles, they do not behave consistently.  The tile at the top
    of the column is the bottom half of a full IOB, and the tile at the bottom
    of the column is the top half of a full IOB.  For this reason, explicit
    bit aliasing is used to map the full IOB bits into the two halves, and a
    mapping is provided for the site naming.

    """

    seen_iobs = set()
    for tile in database:
        if tile in seen_iobs:
            continue

        if database[tile]["type"] not in ["LIOB33", "RIOB33", "RIOB18"]:
            continue

        while True:
            prev_tile = tile
            tile = tiles_by_grid[(
                database[tile]['grid_x'], database[tile]['grid_y'] + 1)]
            if '_SING' in database[tile]['type']:
                break

        bottom_tile = tile
        seen_iobs.add(bottom_tile)

        bits = database[prev_tile]['bits']['CLB_IO_CLK']

        while True:
            tile = tiles_by_grid[(
                database[tile]['grid_x'], database[tile]['grid_y'] - 1)]
            seen_iobs.add(tile)

            if '_SING' in database[tile]['type']:
                break

            if 'CLB_IO_CLK' in database[tile]['bits']:
                assert bits['baseaddr'] == database[tile]['bits'][
                    'CLB_IO_CLK']['baseaddr']
                assert bits['frames'] == database[tile]['bits']['CLB_IO_CLK'][
                    'frames']
                assert bits['words'] == database[tile]['bits']['CLB_IO_CLK'][
                    'words']

        top_tile = tile

        database[top_tile]['bits']['CLB_IO_CLK'] = copy.deepcopy(bits)
        database[top_tile]['bits']['CLB_IO_CLK']['words'] = 2
        database[top_tile]['bits']['CLB_IO_CLK']['offset'] = 99
        database[top_tile]['bits']['CLB_IO_CLK']['alias'] = {
            'type': database[prev_tile]['type'],
            'start_offset': 0,
            'sites': {
                'IOB33_Y0': 'IOB33_Y1',
            }
        }

        database[bottom_tile]['bits']['CLB_IO_CLK'] = copy.deepcopy(bits)
        database[bottom_tile]['bits']['CLB_IO_CLK']['words'] = 2
        database[bottom_tile]['bits']['CLB_IO_CLK']['offset'] = 0
        database[bottom_tile]['bits']['CLB_IO_CLK']['alias'] = {
            'type': database[prev_tile]['type'],
            'start_offset': 2,
            'sites': {
                'IOB33_Y0': 'IOB33_Y0',
            }
        }


def propagate_IOI_SING(database, tiles_by_grid):
    """
    The IOI_SING, similarly to IOB_SING, are half tiles at top and bottom of every
    IO column.

    The tile contains half of the sites that are present in the full IOI,
    namely one ILOGIC, OLOGIC and IDELAY.
    """

    seen_iois = set()
    for tile in database:
        if tile in seen_iois:
            continue

        if database[tile]["type"] not in ["LIOI3", "RIOI3", "RIOI"]:
            continue

        while True:
            prev_tile = tile
            tile = tiles_by_grid[(
                database[tile]['grid_x'], database[tile]['grid_y'] + 1)]
            if '_SING' in database[tile]['type']:
                break

        bottom_tile = tile
        seen_iois.add(bottom_tile)

        bits = database[prev_tile]['bits']['CLB_IO_CLK']

        while True:
            tile = tiles_by_grid[(
                database[tile]['grid_x'], database[tile]['grid_y'] - 1)]
            seen_iois.add(tile)

            if '_SING' in database[tile]['type']:
                break

            if 'CLB_IO_CLK' in database[tile]['bits']:
                if tile.startswith("LIOI") or tile.startswith("RIOI"):
                    assert bits['baseaddr'] == database[tile]['bits'][
                        'CLB_IO_CLK']['baseaddr']
                    assert bits['frames'] == database[tile]['bits'][
                        'CLB_IO_CLK']['frames'], "{}:{} == {}".format(
                            tile, bits['frames'],
                            database[tile]['bits']['CLB_IO_CLK']['frames'])
                    assert bits['words'] == database[tile]['bits'][
                        'CLB_IO_CLK']['words'], "{}: {} != {}".format(
                            tile, bits['words'],
                            database[tile]['bits']['CLB_IO_CLK']['words'])

        top_tile = tile

        database[top_tile]['bits']['CLB_IO_CLK'] = copy.deepcopy(bits)
        database[top_tile]['bits']['CLB_IO_CLK']['words'] = 2
        database[top_tile]['bits']['CLB_IO_CLK']['offset'] = 99
        database[top_tile]['bits']['CLB_IO_CLK']['alias'] = {
            'type': database[prev_tile]['type'],
            'start_offset': 0,
            'sites': {}
        }

        database[bottom_tile]['bits']['CLB_IO_CLK'] = copy.deepcopy(bits)
        database[bottom_tile]['bits']['CLB_IO_CLK']['words'] = 2
        database[bottom_tile]['bits']['CLB_IO_CLK']['offset'] = 0
        database[bottom_tile]['bits']['CLB_IO_CLK']['alias'] = {
            'type': database[prev_tile]['type'],
            'start_offset': 2,
            'sites': {}
        }


def propagate_IOI_Y9(database, tiles_by_grid):
    """
    There are IOI tiles (X0Y9 and X43Y9) that have the frame address 1 frame
    higher than the rest, just like for some of the SING tiles.

    """
    ioi_tiles = os.getenv('XRAY_IOI3_TILES')

    assert ioi_tiles is not None, "XRAY_IOI3_TILES env variable not set"
    tiles = ioi_tiles.split(" ")

    for tile in tiles:
        prev_tile = tiles_by_grid[(
            database[tile]['grid_x'], database[tile]['grid_y'] - 1)]
        while database[prev_tile]["type"] != database[tile]["type"]:
            prev_tile = tiles_by_grid[(
                database[prev_tile]['grid_x'],
                database[prev_tile]['grid_y'] - 1)]
        bits = database[prev_tile]['bits']['CLB_IO_CLK']
        database[tile]['bits']['CLB_IO_CLK'] = copy.deepcopy(bits)
        database[tile]['bits']['CLB_IO_CLK']['words'] = 4
        database[tile]['bits']['CLB_IO_CLK']['offset'] = 18


def alias_HCLKs(database):
    """ Generate HCLK aliases for HCLK_[LR] subsets.

    There are some HCLK_[LR] tiles that are missing some routing due to
    obstructions, e.g. PCIE hardblock.  These tiles do not have southbound
    clock routing, but are otherwise the same as HCLK_[LR] tiles.

    Simply alias their segbits.

    """
    for tile in database:
        if database[tile]['type'] == "HCLK_L_BOT_UTURN":
            database[tile]['bits']['CLB_IO_CLK']['alias'] = {
                "sites": {},
                "start_offset": 0,
                "type": "HCLK_L"
            }
        elif database[tile]['type'] == "HCLK_R_BOT_UTURN":
            database[tile]['bits']['CLB_IO_CLK']['alias'] = {
                "sites": {},
                "start_offset": 0,
                "type": "HCLK_R"
            }


def run(json_in_fn, json_out_fn, verbose=False):
    # Load input files
    database = json.load(open(json_in_fn, "r"))
    tiles_by_grid = make_tiles_by_grid(database)

    tile_frames_map = localutil.TileFrames()
    propagate_INT_lr_bits(
        database, tiles_by_grid, tile_frames_map, verbose=verbose)
    propagate_INT_bits_in_column(database, tiles_by_grid, tile_frames_map)
    propagate_INT_INTERFACE_bits_in_column(
        database, tiles_by_grid, "GTP_INT_INTERFACE", tile_frames_map)
    propagate_INT_INTERFACE_bits_in_column(
        database, tiles_by_grid, "GTX_INT_INTERFACE", tile_frames_map)
    propagate_INT_INTERFACE_bits_in_column(
        database, tiles_by_grid, "PCIE_INT_INTERFACE", tile_frames_map)
    propagate_rebuf(database, tiles_by_grid)
    propagate_IOB_SING(database, tiles_by_grid)
    propagate_IOI_SING(database, tiles_by_grid)
    propagate_IOI_Y9(database, tiles_by_grid)
    alias_HCLKs(database)

    # Save
    xjson.pprint(open(json_out_fn, "w"), database)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate tilegrid.json from bitstream deltas")

    parser.add_argument("--verbose", action="store_true", help="")
    parser.add_argument(
        "--json-in",
        default="tiles_basic.json",
        help="Input .json without addresses")
    parser.add_argument(
        "--json-out", default="tilegrid.json", help="Output JSON")
    args = parser.parse_args()

    run(args.json_in, args.json_out, verbose=args.verbose)


if __name__ == "__main__":
    main()
