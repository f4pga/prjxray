#!/usr/bin/env python3
'''
Take raw .bits files and decode them to higher level functionality
This output is intended for debugging and not directly related to FASM
'''

import sys, os, json, re


class NoDB(Exception):
    pass


# cache
segbitsdb = dict()


# TODO: migrate to library
def get_database(tile_type):
    if tile_type in segbitsdb:
        return segbitsdb[tile_type]

    main_fn = "%s/%s/segbits_%s.db" % (
        os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"),
        tile_type.lower())
    int_fn = "%s/%s/segbits_int_%s.db" % (
        os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"),
        tile_type[-1].lower())

    if not os.path.exists(main_fn) or not os.path.exists(int_fn):
        raise NoDB(tile_type)

    segbitsdb[tile_type] = list()

    with open(main_fn, "r") as f:
        for line in f:
            line = line.split()
            segbitsdb[tile_type].append(line)

    with open(int_fn, "r") as f:
        for line in f:
            line = line.split()
            segbitsdb[tile_type].append(line)

    return segbitsdb[tile_type]


def mk_segbits(seginfo, bitdata):
    baseframe = int(seginfo["baseaddr"][0], 16)
    basewordidx = int(seginfo["baseaddr"][1])
    numframes = int(seginfo["frames"])
    numwords = int(seginfo["words"])

    segbits = set()
    for frame in range(baseframe, baseframe + numframes):
        if frame not in bitdata:
            continue
        for wordidx in range(basewordidx, basewordidx + numwords):
            if wordidx not in bitdata[frame]:
                continue
            for bitidx in bitdata[frame][wordidx]:
                segbits.add(
                    "%02d_%02d" %
                    (frame - baseframe, 32 * (wordidx - basewordidx) + bitidx))
    return segbits


def print_unknown_bits(grid, bitdata):
    '''
    Print bits not covered by known tiles
    '''

    # Index all known locations
    # seggrames[address] = set()
    # where set contains word numbers
    segframes = dict()
    for segname, segdata in grid["segments"].items():
        framebase = int(segdata["baseaddr"][0], 16)
        for i in range(segdata["frames"]):
            words = segframes.setdefault(framebase + i, set())
            for j in range(segdata["baseaddr"][1],
                           segdata["baseaddr"][1] + segdata["words"]):
                words.add(j)

    # print uncovered locations
    print('Non-database bits:')
    for frame in sorted(bitdata.keys()):
        for wordidx in sorted(bitdata[frame].keys()):
            if frame in segframes and wordidx in segframes[frame]:
                continue
            for bitidx in sorted(bitdata[frame][wordidx]):
                print("bit_%08x_%03d_%02d" % (frame, wordidx, bitidx))


def tagmatch(entry, segbits):
    for bit in entry[1:]:
        if bit[0] != "!" and bit not in segbits:
            return False
        if bit[0] == "!" and bit[1:] in segbits:
            return False
    return True


def tag_matched(entry, segbits):
    for bit in entry[1:]:
        if bit[0] != "!":
            segbits.remove(bit)


def seg_decode(flag_decode_emit, seginfo, segbits):
    segtags = set()
    try:
        for entry in get_database(seginfo["type"]):
            if not tagmatch(entry, segbits):
                continue
            tag_matched(entry, segbits)
            if flag_decode_emit:
                segtags.add(entry[0])
    except NoDB:
        print("WARNING: failed to load DB for %s" % seginfo["type"])
    return segtags


def handle_segment(
        segname, grid, bitdata, flag_decode_emit, flag_decode_omit,
        omit_empty_segs):

    assert segname

    # only print bitstream tiles
    if segname not in grid["segments"]:
        return
    seginfo = grid["segments"][segname]

    segbits = mk_segbits(seginfo, bitdata)

    if flag_decode_emit or flag_decode_omit:
        segtags = seg_decode(flag_decode_emit, seginfo, segbits)
    else:
        segtags = set()

    # Found something to print?
    if not (not omit_empty_segs or len(segbits) > 0 or len(segtags) > 0):
        return

    print()
    print("seg %s" % (segname, ))

    for bit in sorted(segbits):
        print("bit %s" % bit)

    for tag in sorted(segtags):
        print("tag %s" % tag)


def load_bitdata(bits_file):
    bitdata = dict()

    with open(bits_file, "r") as f:
        for line in f:
            line = line.split("_")
            frame = int(line[1], 16)
            wordidx = int(line[2], 10)
            bitidx = int(line[3], 10)

            if frame not in bitdata:
                bitdata[frame] = dict()

            if wordidx not in bitdata[frame]:
                bitdata[frame][wordidx] = set()

            bitdata[frame][wordidx].add(bitidx)
    return bitdata


def mk_grid():
    '''Load tilegrid, flattening all blocks into one dictionary'''

    with open("%s/%s/tilegrid.json" % (os.getenv("XRAY_DATABASE_DIR"),
                                       os.getenv("XRAY_DATABASE")), "r") as f:
        new_grid = json.load(f)

    # TODO: Migrate to new tilegrid format via library.
    grid = {'tiles': new_grid, 'segments': {}}

    for tile_name, tile in grid['tiles'].items():
        bits = tile.get('bits', None)
        if not bits:
            continue
        for block_name, block in bits.items():
            segname = mksegment(tile_name, block_name)
            grid['segments'][segname] = {
                'baseaddr': [
                    block['baseaddr'],
                    block['offset'],
                ],
                'type': tile['type'],
                'frames': block['frames'],
                'words': block['words'],
                'tile_name': tile_name,
                'block_name': block_name,
            }
    return grid


def mksegment(tile_name, block_name):
    '''Create a segment name'''
    return '%s:%s' % (tile_name, block_name)


def tile_segnames(grid):
    ret = []
    for tile_name, tile in grid['tiles'].items():
        for block_name in tile['bits'].keys():
            ret.append(mksegment(tile_name, block_name))
    return ret


def run(
        bits_file,
        segnames,
        omit_empty_segs=False,
        flag_unknown_bits=False,
        flag_decode_emit=False,
        flag_decode_omit=False):
    grid = mk_grid()

    bitdata = load_bitdata(bits_file)

    if flag_unknown_bits:
        print_unknown_bits(grid, bitdata)

    # Default: print all
    if segnames:
        for i, segname in enumerate(segnames):
            # Default to common tile config area if tile given without explicit block
            if ':' not in segname:
                segnames[i] = mksegment(segname, 'CLB_IO_CLK')
    else:
        segnames = sorted(tile_segnames(grid))
    print('Segments: %u' % len(segnames))

    # XXX: previously this was sorted by address, not name
    # revisit?
    for segname in segnames:
        handle_segment(
            segname, grid, bitdata, flag_decode_emit, flag_decode_omit,
            omit_empty_segs)


def main():
    import argparse

    # XXX: tool still works, but not well
    # need to eliminate segments entirely
    parser = argparse.ArgumentParser(
        description='XXX: does not print all data?')

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument(
        '-z',
        action='store_true',
        help="do not print a 'seg' header for empty segments")
    parser.add_argument(
        '-b', action='store_true', help='print bits outside of known segments')
    parser.add_argument(
        '-d',
        action='store_true',
        help='decode known segment bits and write them as tags')
    # XXX: possibly broken, or we have missing DB data
    parser.add_argument(
        '-D',
        action='store_true',
        help='decode known segment bits and omit them in the output')
    parser.add_argument('bits_file', help='')
    parser.add_argument(
        'segnames', nargs='*', help='List of tile or tile:block to print')
    args = parser.parse_args()

    run(args.bits_file, args.segnames, args.z, args.b, args.d, args.D)


if __name__ == '__main__':
    main()
