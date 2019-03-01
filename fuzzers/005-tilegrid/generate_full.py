#!/usr/bin/env python3
import copy
import json
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


def propagate_INT_lr_bits(database, tiles_by_grid, verbose=False):
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
            int_words)


def propagate_INT_bits_in_column(database, tiles_by_grid):
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
                    int_frames, int_words)
            elif tile['type'].startswith('INT_'):
                # INT above HCLK
                assert next_tile_type.startswith(
                    'HCLK_{}'.format(l_or_r)), next_tile_type

                offset -= hclk_words
                localutil.add_tile_bits(
                    next_tile, database[next_tile], baseaddr, offset,
                    hclk_frames, hclk_words)
            else:
                # HCLK above INT
                assert tile['type'].startswith(
                    'HCLK_{}'.format(l_or_r)), tile['type']
                if next_tile_type == 'INT_{}'.format(l_or_r):
                    offset -= int_words
                    localutil.add_tile_bits(
                        next_tile, database[next_tile], baseaddr, offset,
                        int_frames, int_words)
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
                    'T_TERM_INT', 'BRKH_INT', 'BRKH_TERM_INT'
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
                    int_frames, int_words)
            elif tile['type'].startswith('INT_'):
                # INT below HCLK
                assert next_tile_type.startswith(
                    'HCLK_{}'.format(l_or_r)), next_tile_type

                offset += int_words
                localutil.add_tile_bits(
                    next_tile, database[next_tile], baseaddr, offset,
                    hclk_frames, hclk_words)
            else:
                # HCLK below INT
                assert tile['type'].startswith(
                    'HCLK_{}'.format(l_or_r)), tile['type']
                assert next_tile_type == 'INT_{}'.format(
                    l_or_r), next_tile_type

                offset += hclk_words
                localutil.add_tile_bits(
                    next_tile, database[next_tile], baseaddr, offset,
                    int_frames, int_words)

            tile_name = next_tile
            tile = database[tile_name]


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
            'offset'] == 47, database[tile_name]['bits']['CLB_IO_CLK']
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

        if database[tile]["type"] not in ["LIOB33", "RIOB33"]:
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


def run(json_in_fn, json_out_fn, verbose=False):
    # Load input files
    database = json.load(open(json_in_fn, "r"))
    tiles_by_grid = make_tiles_by_grid(database)

    propagate_INT_lr_bits(database, tiles_by_grid, verbose=verbose)
    propagate_INT_bits_in_column(database, tiles_by_grid)
    propagate_rebuf(database, tiles_by_grid)
    propagate_IOB_SING(database, tiles_by_grid)

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
