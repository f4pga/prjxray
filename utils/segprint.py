#!/usr/bin/env python3
'''
Take raw .bits files and decode them to higher level functionality
This output is intended for debugging and not directly related to FASM
'''

import sys, os, json, re
from prjxray import bitstream
from prjxray import db as prjxraydb


class NoDB(Exception):
    pass


# cache
segbitsdb = dict()


# int and sites are loaded together so that bit coverage can be checked together
# however, as currently written, each segment is essentially printed twice
def process_db(db, tile_type, process, verbose):
    print(db.get_tile_types())
    ttdb = db.get_tile_type(tile_type)

    fns = [ttdb.tile_dbs.segbits, ttdb.tile_dbs.ppips]
    verbose and print("process_db(%s): %s" % (tile_type, fns))
    for fn in fns:
        if fn:
            with open(fn, "r") as f:
                for line in f:
                    process(line)


def get_database(db, tile_type, verbose=False):
    tags = list()

    if tile_type in segbitsdb:
        return segbitsdb[tile_type]

    def process(l):
        tags.append(l.split())

    process_db(db, tile_type, process, verbose=verbose)

    if len(tags) == 0:
        raise NoDB(tile_type)

    segbitsdb[tile_type] = tags
    return tags


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


def print_unknown_bits(segments, bitdata):
    '''
    Print bits not covered by known tiles
    '''

    # Index all known locations
    # seggrames[address] = set()
    # where set contains word numbers
    segframes = dict()
    for segname, segdata in segments.items():
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


decode_warnings = set()


def seg_decode(flag_decode_emit, db, seginfo, segbits, verbose=False):
    segtags = set()

    # already failed?
    if seginfo["type"] in decode_warnings:
        return segtags

    try:
        for entry in get_database(db, seginfo["type"], verbose=verbose):
            if not tagmatch(entry, segbits):
                continue
            tag_matched(entry, segbits)
            if flag_decode_emit:
                segtags.add(entry[0])
    except NoDB:
        verbose and print(
            "WARNING: failed to load DB for %s" % seginfo["type"])
        decode_warnings.add(seginfo["type"])
    return segtags


def handle_segment(
        db,
        segname,
        segments,
        bitdata,
        flag_decode_emit,
        flag_decode_omit,
        omit_empty_segs,
        verbose=False):

    assert segname

    # only print bitstream tiles
    if segname not in segments:
        return
    seginfo = segments[segname]

    segbits = mk_segbits(seginfo, bitdata)

    if flag_decode_emit or flag_decode_omit:
        segtags = seg_decode(
            flag_decode_emit, db, seginfo, segbits, verbose=verbose)
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


def mk_segments(tiles):
    segments = {}

    for tile_name, tile in tiles.items():
        bits = tile.get('bits', None)
        if not bits:
            continue
        for block_name, block in bits.items():
            segname = mksegment(tile_name, block_name)
            segments[segname] = {
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
    return segments


def mk_grid(db_root):
    with open(os.path.join(db_root, "tilegrid.json"), "r") as f:
        tiles = json.load(f)
    '''Load tilegrid, flattening all blocks into one dictionary'''
    # TODO: Migrate to new tilegrid format via library.
    return tiles, mk_segments(tiles)


def mksegment(tile_name, block_name):
    '''Create a segment name'''
    return '%s:%s' % (tile_name, block_name)


def tile_segnames(tiles):
    ret = []
    for tile_name, tile in tiles.items():
        if 'bits' not in tile:
            continue

        for block_name in tile['bits'].keys():
            ret.append(mksegment(tile_name, block_name))
    return ret


def run(
        db_root,
        bits_file,
        segnames,
        omit_empty_segs=False,
        flag_unknown_bits=False,
        flag_decode_emit=False,
        flag_decode_omit=False,
        verbose=False):
    tiles, segments = mk_grid(db_root)
    db = prjxraydb.Database(db_root)

    bitdata = bitstream.load_bitdata2(open(bits_file, "r"))

    if flag_unknown_bits:
        print_unknown_bits(segments, bitdata)

    # Default: print all
    if segnames:
        for i, segname in enumerate(segnames):
            # Default to common tile config area if tile given without explicit block
            if ':' not in segname:
                segnames[i] = mksegment(segname, 'CLB_IO_CLK')
    else:
        segnames = sorted(tile_segnames(tiles))
    print('Segments: %u' % len(segnames))

    # XXX: previously this was sorted by address, not name
    # revisit?
    for segname in segnames:
        handle_segment(
            db,
            segname,
            segments,
            bitdata,
            flag_decode_emit,
            flag_decode_omit,
            omit_empty_segs,
            verbose=verbose)


def main():
    import argparse

    # XXX: tool still works, but not well
    # need to eliminate segments entirely
    parser = argparse.ArgumentParser(
        description='XXX: does not print all data?')

    database_dir = os.getenv("XRAY_DATABASE_DIR")
    database = os.getenv("XRAY_DATABASE")
    db_root_kwargs = {}
    if database_dir is None or database is None:
        db_root_kwargs['required'] = True
    else:
        db_root_kwargs['required'] = False
        db_root_kwargs['default'] = os.path.join(database_dir, database)

    parser.add_argument('--db_root', help="Database root.", **db_root_kwargs)
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

    run(
        args.db_root, args.bits_file, args.segnames, args.z, args.b, args.d,
        args.D, args.verbose)


if __name__ == '__main__':
    main()
