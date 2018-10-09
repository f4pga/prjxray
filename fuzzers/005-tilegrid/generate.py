#!/usr/bin/env python3
'''
Historically we grouped data into "segments"
These were a region of the bitstream that encoded one or more tiles
However, this didn't scale with certain tiles like BRAM
Some sites had multiple bitstream areas and also occupied multiple tiles

Decoding was then shifted to instead describe how each title is encoded
A post processing step verifies that two tiles don't reference the same bitstream area
'''

import os, sys, json, re

# matches lib/include/prjxray/xilinx/xc7series/block_type.h
block_type_i2s = {
    0: 'CLB_IO_CLK',
    1: 'BLOCK_RAM',
    2: 'CFG_CLB',
    # special...maybe should error until we know what it is?
    # 3: 'RESERVED',
}


def load_tiles(tiles_fn, deltas_fns):
    tiles = list()
    site_baseaddr = dict()
    tile_baseaddr = dict()

    with open(tiles_fn) as f:
        for line in f:
            tiles.append(line.split())

    for arg in deltas_fns:
        with open(arg) as f:
            line = f.read().strip()
            site = arg[7:-6]
            frame = int(line[5:5 + 8], 16)
            site_baseaddr[site] = "0x%08x" % (frame & ~0x7f)

    return tiles, site_baseaddr, tile_baseaddr


def make_database(tiles, site_baseaddr, tile_baseaddr):
    database = dict()
    tiles_by_grid = dict()

    for record in tiles:
        tile_type, tile_name, grid_x, grid_y = record[0:4]
        grid_x, grid_y = int(grid_x), int(grid_y)
        tiles_by_grid[(grid_x, grid_y)] = tile_name
        framebaseaddr = None

        database[tile_name] = {
            "type": tile_type,
            "sites": dict(),
            "grid_x": grid_x,
            "grid_y": grid_y
        }

        if len(record) > 4:
            for i in range(4, len(record), 2):
                site_type, site_name = record[i:i + 2]
                if site_name in site_baseaddr:
                    framebaseaddr = site_baseaddr[site_name]
                database[tile_name]["sites"][site_name] = site_type

        if framebaseaddr is not None:
            tile_baseaddr[tile_name] = [framebaseaddr, 0]

    return database, tiles_by_grid


def make_segments(database, tiles_by_grid, tile_baseaddr):
    '''
    Create segments data structure
    Indicates how tiles are related to bitstream locations
    Also modify database to annotate which segment the tiles belong to

    segments key examples:
        SEG_CLBLM_R_X13Y72
        SEG_BRAM3_L_X6Y85
    '''
    segments = dict()

    for tile_name, tile_data in database.items():
        tile_type = tile_data["type"]
        grid_x = tile_data["grid_x"]
        grid_y = tile_data["grid_y"]

        def add_segment(name, tiles, segtype, frames, words, baseaddr=None):
            assert name not in segments
            segment = segments.setdefault(name, {})
            segment["tiles"] = tiles
            segment["type"] = segtype
            segment["frames"] = frames
            segment["words"] = words
            if baseaddr:
                segment["baseaddr"] = baseaddr

            for tile_name in tiles:
                database[tile_name]["segment"] = name

        def process_clb():
            if tile_type in ["CLBLL_L", "CLBLM_L"]:
                int_tile_name = tiles_by_grid[(grid_x + 1, grid_y)]
            else:
                int_tile_name = tiles_by_grid[(grid_x - 1, grid_y)]

            add_segment(
                name="SEG_" + tile_name,
                tiles=[tile_name, int_tile_name],
                segtype=tile_type.lower(),
                frames=36,
                words=2,
                baseaddr=tile_baseaddr.get(tile_name, None))

        def process_hclk():
            add_segment(
                name="SEG_" + tile_name,
                tiles=[tile_name],
                segtype=tile_type.lower(),
                frames=26,
                words=1)

        def process_bram_dsp():
            for k in range(5):
                if tile_type in ["BRAM_L", "DSP_L"]:
                    interface_tile_name = tiles_by_grid[(
                        grid_x + 1, grid_y - k)]
                    int_tile_name = tiles_by_grid[(grid_x + 2, grid_y - k)]
                elif tile_type in ["BRAM_R", "DSP_R"]:
                    interface_tile_name = tiles_by_grid[(
                        grid_x - 1, grid_y - k)]
                    int_tile_name = tiles_by_grid[(grid_x - 2, grid_y - k)]
                else:
                    assert 0

                if k == 0:
                    tiles = [tile_name, interface_tile_name, int_tile_name]
                else:
                    tiles = [interface_tile_name, int_tile_name]

                add_segment(
                    name="SEG_" + tile_name.replace("_", "%d_" % k, 1),
                    tiles=tiles,
                    segtype=tile_type.lower().replace("_", "%d_" % k, 1),
                    frames=28,
                    words=2)

        {
            "CLBLL_L": process_clb,
            "CLBLL_R": process_clb,
            "CLBLM_L": process_clb,
            "CLBLM_R": process_clb,
            "HCLK_L": process_hclk,
            "HCLK_R": process_hclk,
            "BRAM_L": process_bram_dsp,
            "DSP_L": process_bram_dsp,
            "BRAM_R": process_bram_dsp,
            "DSP_R": process_bram_dsp,
        }.get(tile_type, lambda: None)()

    return segments


def seg_base_addr_lr_INT(database, segments, tiles_by_grid):
    '''Populate segment base addresses: L/R along INT column'''
    for segment_name in segments.keys():
        if "baseaddr" in segments[segment_name]:
            framebase, wordbase = segments[segment_name]["baseaddr"]
            inttile = [
                tile for tile in segments[segment_name]["tiles"]
                if database[tile]["type"] in ["INT_L", "INT_R"]
            ][0]
            grid_x = database[inttile]["grid_x"]
            grid_y = database[inttile]["grid_y"]

            if database[inttile]["type"] == "INT_L":
                grid_x += 1
                framebase = "0x%08x" % (int(framebase, 16) + 0x80)
            else:
                grid_x -= 1
                framebase = "0x%08x" % (int(framebase, 16) - 0x80)

            if (grid_x, grid_y) not in tiles_by_grid:
                continue

            tile = tiles_by_grid[(grid_x, grid_y)]

            if database[inttile]["type"] == "INT_L":
                assert database[tile]["type"] == "INT_R"
            elif database[inttile]["type"] == "INT_R":
                assert database[tile]["type"] == "INT_L"
            else:
                assert 0

            assert "segment" in database[tile]

            seg = database[tile]["segment"]

            if "baseaddr" in segments[seg]:
                assert segments[seg]["baseaddr"] == [framebase, wordbase]
            else:
                segments[seg]["baseaddr"] = [framebase, wordbase]


def seg_base_addr_up_INT(database, segments, tiles_by_grid):
    '''Populate segment base addresses: Up along INT/HCLK columns'''
    start_segments = list()

    for segment_name in segments.keys():
        if "baseaddr" in segments[segment_name]:
            start_segments.append(segment_name)

    for segment_name in start_segments:
        framebase, wordbase = segments[segment_name]["baseaddr"]
        inttile = [
            tile for tile in segments[segment_name]["tiles"]
            if database[tile]["type"] in ["INT_L", "INT_R"]
        ][0]
        grid_x = database[inttile]["grid_x"]
        grid_y = database[inttile]["grid_y"]

        for i in range(50):
            grid_y -= 1

            if wordbase == 50:
                wordbase += 1
            else:
                wordbase += 2

            segname = database[tiles_by_grid[(grid_x, grid_y)]]["segment"]
            segments[segname]["baseaddr"] = [framebase, wordbase]


def base_addr_2_block_type(base_addr):
    '''
    Table 5-24: Frame Address Register Description
    Bit Index: [25:23]
    https://www.xilinx.com/support/documentation/user_guides/ug470_7Series_Config.pdf
    "Valid block types are CLB, I/O, CLK ( 000 ), block RAM content ( 001 ), and CFG_CLB ( 010 ). A normal bitstream does not include type 011 ."
    '''
    block_type_i = (base_addr >> 23) & 0x7
    return block_type_i2s[block_type_i]


def add_tile_bits(tile_db, baseaddr, offset, height):
    '''
    Record data structure geometry for the given tile baseaddr
    For most tiles there is only one baseaddr, but some like BRAM have multiple

    Notes on multiple block types:
    https://github.com/SymbiFlow/prjxray/issues/145
    '''
    bits = tile_db.setdefault('bits', {})
    block_type = base_addr_2_block_type(int(baseaddr, 0))

    assert block_type not in bits
    block = bits.setdefault(block_type, {})

    block["baseaddr"] = baseaddr
    block["offset"] = offset
    block["height"] = height


def add_bits(database, segments):
    '''Transfer segment data into tiles'''
    for segment_name in segments.keys():
        try:
            baseaddr, offset = segments[segment_name]["baseaddr"]
        except:
            print('Failed on segment name %s' % segment_name)
            raise

        for tile_name in segments[segment_name]["tiles"]:
            tile_type = database[tile_name]["type"]
            if tile_type in ["CLBLL_L", "CLBLL_R", "CLBLM_L", "CLBLM_R",
                             "INT_L", "INT_R"]:
                add_tile_bits(database[tile_name], baseaddr, offset, 2)
            elif tile_type in ["HCLK_L", "HCLK_R"]:
                add_tile_bits(database[tile_name], baseaddr, offset, 1)
            elif tile_type in ["BRAM_L", "BRAM_R", "DSP_L", "DSP_R"]:
                add_tile_bits(database[tile_name], baseaddr, offset, 10)
            elif tile_type in ["INT_INTERFACE_L", "INT_INTERFACE_R",
                               "BRAM_INT_INTERFACE_L", "BRAM_INT_INTERFACE_R"]:
                continue
            else:
                # print(tile_type, offset)
                assert False


def annotate_segments(database, segments):
    # TODO: Migrate to new tilegrid format via library.  This data is added for
    # compability with unconverted tools.  Update tools then remove this data from
    # tilegrid.json.
    for tiledata in database.values():
        if "segment" in tiledata:
            segment = tiledata["segment"]
            tiledata["frames"] = segments[segment]["frames"]
            tiledata["words"] = segments[segment]["words"]
            tiledata["segment_type"] = segments[segment]["type"]


def run(tiles_fn, json_fn, deltas_fns):
    tiles, site_baseaddr, tile_baseaddr = load_tiles(tiles_fn, deltas_fns)
    database, tiles_by_grid = make_database(
        tiles, site_baseaddr, tile_baseaddr)
    segments = make_segments(database, tiles_by_grid, tile_baseaddr)
    seg_base_addr_lr_INT(database, segments, tiles_by_grid)
    seg_base_addr_up_INT(database, segments, tiles_by_grid)
    add_bits(database, segments)
    annotate_segments(database, segments)
    json.dump(
        database,
        open(json_fn, 'w'),
        sort_keys=True,
        indent=4,
        separators=(',', ': '))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Generate a simple wrapper to test synthesizing an arbitrary verilog module'
    )

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--out', default='/dev/stdout', help='Output JSON')
    parser.add_argument(
        '--tiles', default='tiles.txt', help='Input tiles.txt tcl output')
    parser.add_argument(
        'deltas', nargs='+', help='.bit diffs to create base addresses from')
    args = parser.parse_args()

    run(args.tiles, args.out, args.deltas)


if __name__ == '__main__':
    main()
