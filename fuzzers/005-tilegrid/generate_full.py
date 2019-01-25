#!/usr/bin/env python3
from __future__ import print_function
import sys, json
from utils import xjson
'''
Historically we grouped data into "segments"
These were a region of the bitstream that encoded one or more tiles
However, this didn't scale with certain tiles like BRAM
Some sites had multiple bitstream areas and also occupied multiple tiles

Decoding was then shifted to instead describe how each title is encoded
A post processing step verifies that two tiles don't reference the same bitstream area
'''

from generate import load_tiles
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


def load_tdb_baseaddr(database, int_tdb, verbose=False):
    tdb_tile_baseaddrs = dict()
    for line in open(int_tdb, 'r'):
        line = line.strip()
        parts = line.split(' ')
        # INT_L_X0Y50.DWORD:0.DBIT:17.DFRAME:14
        tagstr = parts[0]
        # 00000914_000_17 00000918_000_17 ...
        addrlist = parts[1:]
        localutil.check_frames(addrlist)
        frame = localutil.parse_addr(addrlist[0], get_base_frame=True)
        tparts = tagstr.split('.')
        # INT_L_X0Y50
        tile = tparts[0]
        assert tile in database.keys(), "Tile not in Database"
        localutil.add_baseaddr(tdb_tile_baseaddrs, tile, frame, verbose)

    return tdb_tile_baseaddrs


def make_tiles_by_grid(tiles):
    # lookup tile names by (X, Y)
    tiles_by_grid = dict()

    for tile in tiles:
        tiles_by_grid[(tile["grid_x"], tile["grid_y"])] = tile["name"]

    return tiles_by_grid

def add_int_bits(database, tile, baseaddr, offset):
    """
    Add INT bits for given tile.
    """
    if database[tile]['type'] not in ["INT_L", "INT_R"]:
        return

    localutil.add_tile_bits(
        tile, database[tile], baseaddr, offset,
        frames=28, words=2, height=2)

def add_adjacent_int_tiles(database, tiles_by_grid, verbose=False):
    '''
    Attaches INT tiles adjacent to tiles.
    '''

    def add_int_tile(inttile, parent_tile):
        if not database[parent_tile]['bits']:
            return

        grid_x = database[inttile]["grid_x"]
        grid_y = database[inttile]["grid_y"]

        framebase = int(database[parent_tile]['bits']['CLB_IO_CLK']['baseaddr'], 0)
        parent_wordbase = database[parent_tile]['bits']['CLB_IO_CLK']['offset']

        for dst_tile, wordbase in localutil.propagate_up_INT(
                grid_x, grid_y, database, tiles_by_grid, parent_wordbase):
            dst_x = dst_tile['grid_x']
            dst_y = dst_tile['grid_y']

            add_int_bits(
                    database, tiles_by_grid[(dst_x, dst_y)], framebase,
                    wordbase)

    verbose and print('')
    for tile_name, tile_data in database.items():
        tile_type = tile_data["type"]
        grid_x = tile_data["grid_x"]
        grid_y = tile_data["grid_y"]

        def process_clb():
            if tile_type in ["CLBLL_L", "CLBLM_L"]:
                int_tile_name = tiles_by_grid[(grid_x + 1, grid_y)]
            else:
                int_tile_name = tiles_by_grid[(grid_x - 1, grid_y)]

            add_int_tile(int_tile_name, tile_name)

        def process_iob():
            if tile_type.startswith('LIOB'):
                # Two INT_L's
                #add_int_tile(tiles_by_grid[(grid_x + 4, grid_y)], tile_name)
                #add_int_tile(tiles_by_grid[(grid_x + 4, grid_y - 1)], tile_name)
                pass
            else:
                # Two INT_R's
                #add_int_tile(tiles_by_grid[(grid_x - 4, grid_y)], tile_name)
                #add_int_tile(tiles_by_grid[(grid_x - 4, grid_y - 1)], tile_name)
                pass

        def process_iob_sing():
            if tile_type.startswith('LIOB'):
                add_int_tile(tiles_by_grid[(grid_x + 4, grid_y)], tile_name)
            else:
                add_int_tile(tiles_by_grid[(grid_x - 4, grid_y)], tile_name)

        def process_bram_dsp():
            for k in range(5):
                if tile_type in ["BRAM_L", "DSP_L"]:
                    int_tile_name = tiles_by_grid[(grid_x + 2, grid_y - k)]
                elif tile_type in ["BRAM_R", "DSP_R"]:
                    int_tile_name = tiles_by_grid[(grid_x - 2, grid_y - k)]
                else:
                    assert 0

                add_int_tile(int_tile_name, tile_name)

        def process_default():
            verbose and nolr(tile_type) not in (
                'VBRK', 'INT', 'NULL') and print(
                    'make_segment: drop %s' % (tile_type, ))
            pass

        {
            "CLBLL": process_clb,
            "CLBLM": process_clb,
            "HCLK": lambda: None,
            "BRAM": lambda: None,
            "DSP": lambda: None,
            "RIOB33": process_iob,
            "LIOB33": process_iob,
            "RIOB33_SING": process_iob_sing,
            "LIOB33_SING": process_iob_sing,
        }.get(nolr(tile_type), process_default)()


def seg_base_addr_lr_INT(database, tiles_by_grid, verbose=False):
    '''Populate segment base addresses: L/R along INT column'''
    '''
    Create BRAM base addresses based on nearby CLBs
    ie if we have a BRAM_L, compute as nearby CLB_R base address + offset
    '''

    verbose and print('')
    for tile in database:
        if database[tile]["type"] not in ["INT_L", "INT_R"]:
            continue

        if not database[tile]["bits"]:
            continue

        grid_x = database[tile]["grid_x"]
        grid_y = database[tile]["grid_y"]
        framebase = int(database[tile]["bits"]["CLB_IO_CLK"]["baseaddr"], 0)
        wordbase = database[tile]["bits"]["CLB_IO_CLK"]["offset"]

        if database[tile]["type"] == "INT_L":
            grid_x += 1
            framebase = framebase + 0x80
        elif database[tile]["type"] == "INT_R":
            grid_x -= 1
            framebase = framebase - 0x80
        else:
            assert 0

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

        add_int_bits(database, other_tile, framebase, wordbase)


def seg_base_addr_up_INT(database, segments, tiles_by_grid, verbose=False):
    '''Populate segment base addresses: Up along INT/HCLK columns'''

    verbose and print('')
    # Copy the initial list containing only base addresses
    # and soon to have derived addresses
    src_segment_names = list()
    for segment_name in segments.keys():
        if "baseaddr" in segments[segment_name]:
            src_segment_names.append(segment_name)

    verbose and print('up_INT: %u base addresses' % len(src_segment_names))

    for src_segment_name in sorted(src_segment_names):
        src_segment = segments[src_segment_name]

        for block_type, (framebase,
                         wordbase) in sorted(src_segment["baseaddr"].items()):
            verbose and print(
                'up_INT: %s: %s.0x%08X:%u' %
                (src_segment_name, block_type, framebase, wordbase))

            def process_CLB_IO_CLK(wordbase):
                '''
                Lookup interconnect tile associated with this segment
                Use it to locate in the grid, and find other segments related by tile offset
                '''

                for inttile in list(get_inttile(database, src_segment)) + list(
                        get_iobtile(database, src_segment)):
                    verbose and print(
                        '  up_INT CLK_IO_CLK: %s => inttile %s' %
                        (src_segment_name, inttile),
                        file=sys.stderr)
                    grid_x = database[inttile]["grid_x"]
                    grid_y = database[inttile]["grid_y"]

                    for dst_tile, wordbase in localutil.propagate_up_INT(
                            grid_x, grid_y, database, tiles_by_grid, wordbase):
                        if 'segment' not in dst_tile:
                            print(
                                'WARNING: Missing segment for {} ({}, {}) {}'.
                                format(
                                    tiles_by_grid[(grid_x, grid_y)], grid_x,
                                    grid_y, dst_tile))
                            continue

                        #verbose and print('  dst_tile', dst_tile)
                        if 'segment' in dst_tile:
                            dst_segment_name = dst_tile["segment"]
                        #verbose and print('up_INT: %s => %s' % (src_segment_name, dst_segment_name))
                        segments[dst_segment_name].setdefault(
                            "baseaddr",
                            {})[block_type] = [framebase, wordbase]

            def process_BLOCK_RAM(wordbase):
                '''
                Lookup BRAM0 tile associated with this segment
                Use it to locate in the grid, and find other BRAM0 related by tile offset
                From minitest:
                build/roi_bramd_bit01.diff (lowest BRAM coordinate)
                > bit_00c00000_000_00
                build/roi_bramds_bit01.diff
                > bit_00c00000_000_00
                > bit_00c00000_010_00
                > bit_00c00000_020_00
                > bit_00c00000_030_00
                > bit_00c00000_040_00
                > bit_00c00000_051_00
                > bit_00c00000_061_00
                > bit_00c00000_071_00
                > bit_00c00000_081_00
                > bit_00c00000_091_00
                '''
                src_tile_name = get_bramtile(database, src_segment)
                verbose and print(
                    '  up_INT BLOCK_RAM: %s => %s' %
                    (src_segment_name, src_tile_name))
                grid_x = database[src_tile_name]["grid_x"]
                grid_y = database[src_tile_name]["grid_y"]

                for i in range(9):
                    grid_y -= 5
                    wordbase += 10
                    # Skip HCLK
                    if i == 4:
                        grid_y -= 1
                        wordbase += 1

                    # FIXME: PCIE block cuts out some BRAM
                    # this messes up algorithm  as is and may cause this to fail
                    if grid_y < 0:
                        continue

                    dst_tile_name = tiles_by_grid[(grid_x, grid_y)]

                    dst_tile = database[dst_tile_name]
                    assert nolr(dst_tile['type']) == 'BRAM', dst_tile

                    dst_segment_name = dst_tile["segment"]
                    verbose and print(
                        '  up_INT BLOCK_RAM: %s => %s' %
                        (dst_segment_name, dst_tile_name))
                    assert 'BRAM0' in dst_segment_name
                    segments[dst_segment_name].setdefault(
                        "baseaddr", {})[block_type] = [framebase, wordbase]

            {
                'CLB_IO_CLK': process_CLB_IO_CLK,
                'BLOCK_RAM': process_BLOCK_RAM,
            }[block_type](
                wordbase)


def db_add_bits(database, segments):
    '''Transfer segment data into tiles'''
    for segment_name in segments.keys():
        if 'baseaddr' not in segments[segment_name]:
            continue

        for block_type, (baseaddr,
                         offset) in segments[segment_name]["baseaddr"].items():
            for tile_name in segments[segment_name]["tiles"]:
                tile_type = database[tile_name]["type"]

                entry = localutil.get_entry(nolr(tile_type), block_type)

                if entry is None:
                    # Other types are rare, not expected to have these
                    if block_type == "CLB_IO_CLK":
                        raise ValueError("Unknown tile type %s" % tile_type)
                    continue

                frames, words, height = entry
                if frames:
                    # if we have a width, we should have a height
                    assert frames and words
                    localutil.add_tile_bits(
                        tile_name, database[tile_name], baseaddr, offset,
                        frames, words, height)


def db_add_segments(database, segments):
    # TODO: Migrate to new tilegrid format via library.  This data is added for
    # compability with unconverted tools.  Update tools then remove this data from
    # tilegrid.json.
    # looks like only htmlgen is using this?
    for tiledata in database.values():
        if "segment" in tiledata:
            segment = tiledata["segment"]
            tiledata["segment_type"] = segments[segment]["type"]


def db_int_fixup(database, tiles, tiles_by_grid):
    for tile_name in tiles.keys():
        tiles_to_add = dict()

        tile = database[tile_name]
        grid_x = tile["grid_x"]
        grid_y = tile["grid_y"]

        tile_type = tile["type"]

        block_type, (baseaddr, offset) = sorted(tiles[tile_name].items())[0]

        frames, words, height = localutil.get_entry(
            nolr(tile_type), block_type)
        # Adding first bottom INT tile
        localutil.add_tile_bits(
            tile_name, tile, baseaddr, offset, frames, words, height)

        for tile, offset in localutil.propagate_up_INT(
                grid_x, grid_y, database, tiles_by_grid, offset):
            localutil.add_tile_bits(
                tile_name, tile, baseaddr, offset, frames, words, height)


def run(json_in_fn, json_out_fn, tiles_fn, int_tdb=None, verbose=False):
    # Load input files
    tiles = load_tiles(tiles_fn)
    #site_baseaddr = {}
    database = json.load(open(json_in_fn, "r"))

    tiles_by_grid = make_tiles_by_grid(tiles)

    if int_tdb is not None:
        tile_baseaddrs_fixup = load_tdb_baseaddr(database, int_tdb)
        db_int_fixup(database, tile_baseaddrs_fixup, tiles_by_grid)

    #add_adjacent_int_tiles(database, tiles_by_grid, verbose=verbose)

    # Reference adjacent CLBs to locate adjacent tiles by known offsets
    #seg_base_addr_lr_INT(database, tiles_by_grid, verbose=verbose)

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
    parser.add_argument(
        '--tiles', default='tiles.txt', help='Input tiles.txt tcl output')
    parser.add_argument(
        "--int-tdb",
        default=None,
        help=".tdb diffs to fill the interconnects without any adjacent CLB")
    args = parser.parse_args()

    run(
        args.json_in,
        args.json_out,
        args.tiles,
        args.int_tdb,
        verbose=args.verbose)


if __name__ == "__main__":
    main()
