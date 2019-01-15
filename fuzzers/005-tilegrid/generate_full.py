#!/usr/bin/env python3
import os, sys, json, re
'''
Historically we grouped data into "segments"
These were a region of the bitstream that encoded one or more tiles
However, this didn't scale with certain tiles like BRAM
Some sites had multiple bitstream areas and also occupied multiple tiles

Decoding was then shifted to instead describe how each title is encoded
A post processing step verifies that two tiles don't reference the same bitstream area
'''

from generate import load_tiles
from prjxray import util
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


def load_baseaddrs(deltas_fns):
    site_baseaddr = dict()
    for arg in deltas_fns:
        with open(arg) as f:
            line = f.read().strip()
            # clb/design_SLICE_X10Y100.delta
            # site = arg[7:-6]
            site = re.match(r".*/design_(.*).delta", arg).group(1)
            # +bit_00400026_100_02
            _, frame_str, _, _ = line.split('_')
            frame = int(frame_str, 16)
            site_baseaddr[site] = frame & ~0x7f

    return site_baseaddr


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


def make_tile_baseaddrs(tiles, site_baseaddr, verbose=False):
    # Look up a base address by tile name
    tile_baseaddrs = dict()
    verbose and print('')
    verbose and print('%u tiles' % len(tiles))
    verbose and print("%u baseaddrs" % len(site_baseaddr))
    added = 0
    for tile in tiles:
        for site_name in tile["sites"].keys():
            if site_name not in site_baseaddr:
                continue
            framebaseaddr = site_baseaddr[site_name]
            localutil.add_baseaddr(
                tile_baseaddrs, tile["name"], framebaseaddr, verbose)
            added += 1

    assert added, "Failed to add any base addresses"
    assert added == len(site_baseaddr)
    return tile_baseaddrs


def make_tiles_by_grid(tiles):
    # lookup tile names by (X, Y)
    tiles_by_grid = dict()

    for tile in tiles:
        tiles_by_grid[(tile["grid_x"], tile["grid_y"])] = tile["name"]

    return tiles_by_grid


def add_segment(
        database, segments, name, tiles, segtype, verbose, baseaddr=None):
    assert name not in segments
    segment = segments.setdefault(name, {})
    segment["tiles"] = tiles
    segment["type"] = segtype
    if baseaddr:
        verbose and print('make_segment: %s baseaddr %s' % (
            name,
            baseaddr,
        ))
        segment["baseaddr"] = baseaddr

    for tile_name in tiles:
        database[tile_name]["segment"] = name


def make_segments(database, tiles_by_grid, tile_baseaddrs, verbose=False):
    '''
    Create segments data structure
    Indicates how tiles are related to bitstream locations
    Also modify database to annotate which segment the tiles belong to
    segments key examples:
        SEG_CLBLM_R_X13Y72
        SEG_BRAM3_L_X6Y85
    '''
    segments = dict()

    verbose and print('')
    for tile_name, tile_data in database.items():
        tile_type = tile_data["type"]
        grid_x = tile_data["grid_x"]
        grid_y = tile_data["grid_y"]

        def add_segment(tiles, segtype, name=None, baseaddr=None):
            assert name not in segments
            segment = segments.setdefault(name, {})
            segment["tiles"] = tiles
            segment["type"] = segtype
            if baseaddr:
                verbose and print(
                    'make_segment: %s baseaddr %s' % (
                        name,
                        baseaddr,
                    ))
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
                baseaddr=tile_baseaddrs.get(tile_name, None))

        def process_hclk():
            add_segment(
                name="SEG_" + tile_name,
                tiles=[tile_name],
                segtype=tile_type.lower())

        def process_iob():
            tiles = [tile_name]
            # FIXME mcmaster: removing INT for now
            # Geometry doesn't line up with CLB, unclear if they are included
            if tile_type.startswith('LIOB'):
                # Two INT_L's
                # tiles.append(tiles_by_grid[(grid_x + 4, grid_y)])
                # tiles.append(tiles_by_grid[(grid_x + 4, grid_y - 1)])
                # One IO interface tile
                tiles.append(tiles_by_grid[(grid_x + 1, grid_y)])
            else:
                # Two INT_R's
                # tiles.append(tiles_by_grid[(grid_x - 4, grid_y)])
                # tiles.append(tiles_by_grid[(grid_x - 4, grid_y - 1)])
                # One IO interface tile
                tiles.append(tiles_by_grid[(grid_x - 1, grid_y)])

            add_segment(
                name="SEG_" + tile_name,
                tiles=tiles,
                segtype=tile_type.lower(),
                baseaddr=tile_baseaddrs.get(tile_name, None))

        def process_iob_sing():
            # FIXME mcmaster: removing INT for now
            # Geometry doesn't line up with CLB, unclear if they are included
            tiles = [tile_name]
            if tile_type.startswith('LIOB'):
                tiles.append(tiles_by_grid[(grid_x + 1, grid_y)])
                # tiles.append(tiles_by_grid[(grid_x + 4, grid_y)])
            else:
                tiles.append(tiles_by_grid[(grid_x - 1, grid_y)])
                # tiles.append(tiles_by_grid[(grid_x - 4, grid_y)])

            add_segment(
                name="SEG_" + tile_name,
                tiles=tiles,
                segtype=tile_type.lower(),
                baseaddr=tile_baseaddrs.get(tile_name, None))

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
                '''
                BRAM/DSP itself is at the base y address
                There is one huge switchbox on the right for the 5 tiles
                These fan into 5 BRAM_INT_INTERFACE tiles each which feed into their own CENTER_INTER (just like a CLB has)
                '''
                if k == 0:
                    tiles = [tile_name, interface_tile_name, int_tile_name]
                    baseaddr = tile_baseaddrs.get(tile_name, None)
                else:
                    tiles = [interface_tile_name, int_tile_name]
                    baseaddr = None

                add_segment(
                    # BRAM_L_X6Y70 => SEG_BRAM4_L_X6Y70
                    name="SEG_" + tile_name.replace("_", "%d_" % k, 1),
                    tiles=tiles,
                    # BRAM_L => bram4_l
                    segtype=tile_type.lower().replace("_", "%d_" % k, 1),
                    baseaddr=baseaddr)

        def process_default():
            verbose and nolr(tile_type) not in (
                'VBRK', 'INT', 'NULL') and print(
                    'make_segment: drop %s' % (tile_type, ))
            pass

        """
        FIXME: review IOB
            "RIOB33": process_iob,
            "LIOB33": process_iob,
            "RIOB33_SING": process_iob_sing,
            "LIOB33_SING": process_iob_sing,
        """
        {
            "CLBLL": process_clb,
            "CLBLM": process_clb,
            "HCLK": process_hclk,
            "BRAM": process_bram_dsp,
            "DSP": process_bram_dsp,
        }.get(nolr(tile_type), process_default)()

    return segments


def get_inttile(database, segment):
    '''Return interconnect tile for given segment'''
    return (
        tile for tile in segment["tiles"]
        if database[tile]["type"] in ["INT_L", "INT_R"])


def get_iobtile(database, segment):
    '''Return IOB tile for given segment'''
    return (
        tile for tile in segment["tiles"]
        if database[tile]["type"] in ["LIOB33_SING", "LIOB33"])


def get_bramtile(database, segment):
    inttiles = [
        tile for tile in segment["tiles"]
        if database[tile]["type"] in ["BRAM_L", "BRAM_R"]
    ]
    assert len(inttiles) == 1
    return inttiles[0]


def create_segment_for_int_lr(
        database, segments, tile, tiles_by_grid, verbose):
    """ Creates INT_[LR] segment for interconnect's without direct connectivity. """
    # Some INT_[LR] tiles have no adjacent connectivity, create a segment.
    grid_x = database[tile]["grid_x"]
    grid_y = database[tile]["grid_y"]
    if database[tile]["type"] == "INT_L":
        grid_x -= 1
        adjacent_tile = tiles_by_grid[(grid_x, grid_y)]
    elif database[tile]["type"] == "INT_R":
        grid_x += 1
        adjacent_tile = tiles_by_grid[(grid_x, grid_y)]
    else:
        assert False, database[tile]["type"]
    if (database[adjacent_tile]['type'].startswith('INT_INTERFACE_') or
            database[adjacent_tile]['type'].startswith('PCIE_INT_INTERFACE_')
            or
            database[adjacent_tile]['type'].startswith('GTP_INT_INTERFACE')):
        # This INT_[LR] tile has no adjacent connectivity,
        # create a segment.
        add_segment(
            database=database,
            segments=segments,
            name='SEG_' + tile,
            tiles=[tile],
            segtype=database[tile]["type"],
            verbose=verbose,
        )
    else:
        assert False, database[adjacent_tile]['type']


def seg_base_addr_lr_INT(database, segments, tiles_by_grid, verbose=False):
    '''Populate segment base addresses: L/R along INT column'''
    '''
    Create BRAM base addresses based on nearby CLBs
    ie if we have a BRAM_L, compute as nearby CLB_R base address + offset
    '''

    verbose and print('')
    for segment_name in sorted(segments.keys()):
        segment = segments[segment_name]
        baseaddrs = segment.get("baseaddr", None)
        if not baseaddrs:
            continue

        for block_type, (framebase, wordbase) in sorted(baseaddrs.items()):
            verbose and print(
                'lr_INT: %s: %s.0x%08X:%u' %
                (segment_name, block_type, framebase, wordbase))
            if block_type != 'CLB_IO_CLK':
                verbose and print('  Skip non CLB')
                continue

            for inttile in get_inttile(database, segment):
                grid_x = database[inttile]["grid_x"]
                grid_y = database[inttile]["grid_y"]

                if database[inttile]["type"] == "INT_L":
                    grid_x += 1
                    framebase = framebase + 0x80
                elif database[inttile]["type"] == "INT_R":
                    grid_x -= 1
                    framebase = framebase - 0x80
                else:
                    assert 0

                # ROI at edge?
                if (grid_x, grid_y) not in tiles_by_grid:
                    verbose and print('  Skip edge')
                    continue

                tile = tiles_by_grid[(grid_x, grid_y)]

                if database[inttile]["type"] == "INT_L":
                    assert database[tile]["type"] == "INT_R"
                elif database[inttile]["type"] == "INT_R":
                    assert database[tile]["type"] == "INT_L"
                else:
                    assert 0

                if "segment" not in database[tile]:
                    continue

                seg = database[tile]["segment"]

                seg_baseaddrs = segments[seg].setdefault("baseaddr", {})
                # At least one duplicate when we re-compute the entry for the base address
                # should give the same address
                if block_type in seg_baseaddrs:
                    assert seg_baseaddrs[block_type] == [
                        framebase, wordbase
                    ], (seg_baseaddrs[block_type], [framebase, wordbase])
                    verbose and print('  Existing OK')
                else:
                    seg_baseaddrs[block_type] = [framebase, wordbase]
                    verbose and print('  Add new')


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
                        assert 'segment' in dst_tile, (
                            (grid_x, grid_y), dst_tile,
                            tiles_by_grid[(grid_x, grid_y)])

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


def run(json_in_fn, json_out_fn, tiles_fn, deltas_fns, int_tdb=None, verbose=False):
    # Load input files
    tiles = load_tiles(tiles_fn)
    site_baseaddr = load_baseaddrs(deltas_fns)
    database = json.load(open(json_in_fn, "r"))

    tile_baseaddrs = make_tile_baseaddrs(tiles, site_baseaddr, verbose=verbose)
    tiles_by_grid = make_tiles_by_grid(tiles)

    segments = make_segments(
        database, tiles_by_grid, tile_baseaddrs, verbose=verbose)

    # Reference adjacent CLBs to locate adjacent tiles by known offsets
    seg_base_addr_lr_INT(database, segments, tiles_by_grid, verbose=verbose)
    seg_base_addr_up_INT(database, segments, tiles_by_grid, verbose=verbose)

    db_add_bits(database, segments)
    db_add_segments(database, segments)

    if int_tdb is not None:
        tile_baseaddrs_fixup = load_tdb_baseaddr(database, int_tdb)
        db_int_fixup(database, tile_baseaddrs_fixup, tiles_by_grid)

    # Save
    json.dump(
        database,
        open(json_out_fn, "w"),
        sort_keys=True,
        indent=4,
        separators=(",", ": "))


def main():
    import argparse
    import glob

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
        "deltas", nargs="*", help=".bit diffs to create base addresses from")
    parser.add_argument(
        "--int-tdb",
        default=None,
        help=".tdb diffs to fill the interconnects without any adjacent CLB")
    args = parser.parse_args()

    deltas = args.deltas
    if not args.deltas:
        deltas = glob.glob("*.delta")

    run(
        args.json_in,
        args.json_out,
        args.tiles,
        deltas,
        args.int_tdb,
        verbose=args.verbose)


if __name__ == "__main__":
    main()
