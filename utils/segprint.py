#!/usr/bin/env python3

import sys, os, json, re


class NoDB(Exception):
    pass


# cache
segbitsdb = dict()


def get_database(segtype):
    if segtype in segbitsdb:
        return segbitsdb[segtype]

    main_fn = "%s/%s/segbits_%s.db" % (
        os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"),
        segtype.lower())
    int_fn = "%s/%s/segbits_int_%s.db" % (
        os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"),
        segtype[-1].lower())

    if not os.path.exists(main_fn) or not os.path.exists(int_fn):
        raise NoDB(segtype)

    segbitsdb[segtype] = list()

    with open(main_fn, "r") as f:
        for line in f:
            line = line.split()
            segbitsdb[segtype].append(line)

    with open(int_fn, "r") as f:
        for line in f:
            line = line.split()
            segbitsdb[segtype].append(line)

    return segbitsdb[segtype]


def handle_split_segment(
        segname, grid, bitdata, flag_d, flag_D, omit_empty_segs):
    seg1, seg2 = segname.split(":")

    if seg1 in grid["tiles"]:
        seg1 = grid["tiles"][seg1]["segment"]

    if seg2 in grid["tiles"]:
        seg2 = grid["tiles"][seg2]["segment"]

    seginfo1 = grid["segments"][seg1]
    seginfo2 = grid["segments"][seg2]

    frame1 = int(seginfo1["baseaddr"][0], 16)
    word1 = int(seginfo1["baseaddr"][1])

    frame2 = int(seginfo2["baseaddr"][0], 16)
    word2 = int(seginfo2["baseaddr"][1])

    if frame1 > frame2:
        frame1, frame2 = frame2, frame1

    if word1 > word2:
        word1, word2 = word2, word1

    segs = list()

    for seg, seginfo in sorted(grid["segments"].items()):
        frame = int(seginfo["baseaddr"][0], 16)
        word = int(seginfo["baseaddr"][1])
        if frame1 <= frame <= frame2 and word1 <= word <= word2:
            segs.append((frame, word, seg))

    for _, _, seg in sorted(segs):
        handle_segment(segname, grid, bitdata, flag_d, flag_D, omit_empty_segs)


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


def seg_decode(flag_d, seginfo, segbits, segtags):
    try:
        for entry in get_database(seginfo["type"]):
            match_entry = True
            for bit in entry[1:]:
                if bit[0] != "!" and bit not in segbits:
                    match_entry = False
                if bit[0] == "!" and bit[1:] in segbits:
                    match_entry = False
            if match_entry:
                for bit in entry[1:]:
                    if bit[0] != "!":
                        segbits.remove(bit)
                if flag_d:
                    segtags.add(entry[0])
    except NoDB:
        print("WARNING: failed to load DB for %s" % seginfo["type"])


def handle_segment(segname, grid, bitdata, flag_d, flag_D, omit_empty_segs):
    '''
    segname: tile name
    '''

    assert segname

    # ? probably legacy
    #if ":" in segname:
    #    handle_split_segment(segname, grid, bitdata, flag_d, flag_D, omit_empty_segs)
    #    return

    # compatibility?
    # now dealing only with tile names...?
    #if segname in grid["tiles"]:
    #    segname = grid["tiles"][segname]["segment"]

    # only print bitstream tiles
    if segname not in grid["segments"]:
        return
    seginfo = grid["segments"][segname]

    segtags = set()
    segbits = mk_segbits(seginfo, bitdata)

    if flag_d or flag_D:
        seg_decode(flag_d, seginfo, segbits, segtags)

    # Found something to print?
    if not omit_empty_segs or len(segbits) > 0 or len(segtags) > 0:
        print()
        print("tile %s" % segname)

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
    with open("%s/%s/tilegrid.json" % (os.getenv("XRAY_DATABASE_DIR"),
                                       os.getenv("XRAY_DATABASE")), "r") as f:
        new_grid = json.load(f)

    # TODO: Migrate to new tilegrid format via library.
    grid = {'tiles': new_grid, 'segments': {}}

    for tile_name, tile in grid['tiles'].items():
        bits = tile.get('bits', None)
        if not bits:
            continue
        block = bits.get('CLB_IO_CLK', None)
        if not block:
            continue

        grid['segments'][tile_name] = {
            'baseaddr': [
                block['baseaddr'],
                block['offset'],
            ],
            'type': tile['type'],
            'frames': block['frames'],
            'words': block['words'],
        }
    return grid


def run(
        bits_file,
        segments,
        omit_empty_segs=False,
        flag_b=False,
        flag_d=False,
        flag_D=False):
    grid = mk_grid()

    bitdata = load_bitdata(bits_file)

    if flag_b:
        print_unknown_bits(grid, bitdata)

    if segments:
        for segment in segments:
            handle_segment(
                segment, grid, bitdata, flag_d, flag_D, omit_empty_segs)
    else:
        for segname in sorted(grid['tiles'].keys()):
            handle_segment(
                segname, grid, bitdata, flag_d, flag_D, omit_empty_segs)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='')

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
    parser.add_argument('segments', nargs='*', help='')
    args = parser.parse_args()

    run(args.bits_file, args.segments, args.z, args.b, args.d, args.D)


if __name__ == '__main__':
    main()
