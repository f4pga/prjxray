#!/usr/bin/env python3
'''
Take raw .bits files and decode them to higher level functionality

A segment as currently used is defined as a tile type + a memory region
Ex: BRAM_L_X6Y100:CLB_IO_CLK
'''

import sys, os, json, re
from prjxray import bitstream
from prjxray import db as prjxraydb
from prjxray import util


class NoDB(Exception):
    pass


# cache
segbitsdb = dict()


# int and sites are loaded together so that bit coverage can be checked together
# however, as currently written, each segment is essentially printed twice
def process_db(db, tile_type, process, verbose):
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
        # l like: CLBLL_L.SLICEL_X0.AMUX.CY !30_07 !30_11 30_06 30_08
        # Parse tags to do math when multiple tiles share an address space
        parts = l.split()
        name = parts[0]

        def parsetag(x):
            # !30_07
            if x[0] == '!':
                isset = False
                numstr = x[1:]
            else:
                isset = True
                numstr = x
            frame, word = numstr.split("_")
            # second part forms a tuple refereced in sets
            return (isset, (int(frame, 10), int(word, 10)))

        if parts[1] == 'always' or parts[1] == 'hint':
            tagbits = []
        else:
            tagbits = [parsetag(x) for x in parts[1:]]

        tags.append(list([name] + tagbits))

    process_db(db, tile_type, process, verbose=verbose)

    if len(tags) == 0:
        raise NoDB(tile_type)

    segbitsdb[tile_type] = tags
    return tags


def mk_segbits(seginfo, bitdata):
    '''
    Given a tile memory region (seginfo), return list of bits in that region

    seginfo: mk_segments()s object supplying address range
    bitdata: all bits in the entire bitstream
    '''

    segbits = set()

    block = seginfo["block"]
    baseaddr = int(block["baseaddr"], 0)
    frames = block["frames"]
    word_offset = block["offset"]
    words = block["words"]

    for frame in range(baseaddr, baseaddr + frames):
        if frame not in bitdata:
            continue
        for wordidx in range(word_offset, word_offset + words):
            if wordidx not in bitdata[frame]:
                continue
            for bitidx in bitdata[frame][wordidx]:
                frame_addr = frame - baseaddr
                bit_addr = 32 * (wordidx - word_offset) + bitidx
                #segbits.add( "%02d_%02d" % (frame_addr, word_addr))
                segbits.add((frame_addr, bit_addr))

    return segbits


def print_unknown_bits(segments, bitdata):
    '''
    Print bits not covered by known tiles
    '''

    # Index all known locations
    # seggrames[address] = set()
    # where set contains word numbers
    segframes = dict()
    for segname, segment in segments.items():
        block = segment["block"]
        framebase = int(block["baseaddr"][0], 16)
        for i in range(block["frames"]):
            words = segframes.setdefault(framebase + i, set())
            for j in range(block["baseaddr"][1],
                           block["baseaddr"][1] + block["words"]):
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
    '''Does tag appear in segbits?'''

    # Entry like "CLBLL_L.SLICEL_X0.AMUX.CY !30_07 !30_11 30_06 30_08".split()
    for bit in entry[1:]:
        isset, bitaddr = bit

        # Reject if bit polarity is incorrect
        if bitaddr not in segbits if isset else bitaddr in segbits:
            return False
    return True


def tag_matched(entry, segbits):
    for bit in entry[1:]:
        isset, bitaddr = bit
        if isset:
            segbits.remove(bitaddr)


# tile types that failed to decode
decode_warnings = set()


def seg_decode(db, seginfo, segbits, segments, verbose=False):
    '''
    Remove matched tags from segbits
    Returns a list of all matched tags
    '''

    segtags = set()

    # Valid addresses for refereced tiles
    ref_block = seginfo["block"]
    # ref_frame_as = (int(ref_block["baseaddr"], 0), int(ref_block["baseaddr"], 0) + ref_block["frames"] - 1)
    ref_frame_as = (0, ref_block["frames"] - 1)
    ref_bit_as = (
        32 * ref_block["offset"],
        32 * (ref_block["offset"] + ref_block["words"]) - 1)

    def process(cmp_seginfo, ref_tile_name):
        tile_type = cmp_seginfo["tile"]["type"]

        # already failed?
        if tile_type in decode_warnings:
            return

        try:
            entries = get_database(db, tile_type, verbose=verbose)
        except NoDB:
            verbose and print("WARNING: failed to load DB for %s" % tile_type)
            assert tile_type != 'BRAM_L'
            decode_warnings.add(tile_type)
            return

        cmp_block = cmp_seginfo["block"]
        ref_frame_delta = int(cmp_block["baseaddr"], 0) - int(
            ref_block["baseaddr"], 0)
        ref_bit_delta = 32 * (cmp_block["offset"] - ref_block["offset"])

        def adjust_entry_addr(entry):
            '''Return bits that apply to this tile at the correct address'''
            tagname = entry[0]
            bits = entry[1:]
            if len(bits) == 0:
                return None
            ret = [tagname]

            def adjust_entry():
                '''Adjust entry in another tile address space to be in our reference tile address space'''
                for isset, old_bitaddr, in bits:
                    old_frame_addr, old_bit_addr = old_bitaddr
                    new_frame_addr = old_frame_addr + ref_frame_delta
                    if not (ref_frame_as[0] <= new_frame_addr <=
                            ref_frame_as[1]):
                        verbose and print(
                            "out frame range: %d <= %d <= %d" %
                            (ref_frame_as[0], new_frame_addr, ref_frame_as[1]))
                        return False

                    new_bit_addr = old_bit_addr + ref_bit_delta
                    # Verify in range of original tile
                    # This can happen if a smaller tile references a larger tile
                    if not (ref_bit_as[0] <= new_bit_addr <= ref_bit_as[1]):
                        verbose and print(
                            "out bit range: %d <= %d <= %d" %
                            (ref_bit_as[0], new_bit_addr, ref_bit_as[1]))
                        return False
                    ret.append((isset, (new_frame_addr, new_bit_addr)))
                    verbose and print(
                        "ent %02d_%02d => %02d_%02d" % (
                            old_frame_addr, old_bit_addr, new_frame_addr,
                            new_bit_addr))
                return True

            if not adjust_entry():
                return None
            return ret

        for entry in entries:
            if ref_tile_name:
                entry = adjust_entry_addr(entry)
                if entry is None:
                    continue
                verbose and print('adjusted entry', entry)

            if not tagmatch(entry, segbits):
                continue
            tag_matched(entry, segbits)
            tagname = entry[0]
            # Prefix matches not from this tile
            if ref_tile_name:
                segtags.add('%s:%s' % (ref_tile_name, tagname))
            else:
                segtags.add(tagname)

    # Reference tile
    process(seginfo, None)
    # Tiles that share our address space
    for (ref_tile_name, cmp_block_name) in seginfo['segtiles']:
        process(
            segments[mksegment(ref_tile_name, cmp_block_name)], ref_tile_name)

    return segtags


def print_seg(segname, segbits, segtags, decode_emit):
    '''Print segment like used by segmaker/segmatch'''

    print("seg %s" % (segname, ))

    # Bits that weren't decoded
    for bit in sorted(segbits):
        print("bit %02d_%02d" % bit)

    if decode_emit:
        for tag in sorted(segtags):
            print("tag %s" % tag)


def handle_segment(
        db,
        segname,
        bitdata,
        decode_emit,
        decode_omit,
        omit_empty_segs,
        segments,
        verbose=False):

    seginfo = segments[segname]

    # only print bitstream tiles
    #if segname not in segments:
    #    return

    segbits = mk_segbits(seginfo, bitdata)

    if decode_emit or decode_omit:
        segtags = seg_decode(db, seginfo, segbits, segments, verbose=verbose)
    else:
        segtags = set()

    # Found something to print?
    if not (not omit_empty_segs or len(segbits) > 0 or len(segtags) > 0):
        return

    print()
    print_seg(segname, segbits, segtags, decode_emit)


def overlap(a, b):
    return a[0] <= b[0] <= a[1] or b[0] <= a[0] <= b[1]


def mk_segtiles(tiles):
    '''
    Return a dictionary of tile_name:tiles
    Where tiles is a list of tiles that are in our address space

    Assumption: tiles in the same minor address region have the same base address and number frames

    As DB is written, not all have the same number of frames
    Ex: CLBLM_R_X7Y108 36 frames, INT_R_X7Y108 28 frames
    We could check for this, but don't think its worth the effort
    Maybe this should be corrected in the DB?
    '''

    segtiles = {}

    # Group by base address
    baseaddrs = {}
    for tile_name, tile in tiles.items():
        for block_name, block in tile['bits'].items():
            baseaddrs.setdefault(block["baseaddr"], []).append(
                (block["offset"], tile_name, block, block_name))

    for baseaddr, values in baseaddrs.items():
        '''
        There are only 256 addresses per minor address
        Just do a set brute force search for now?
        Maybe too slow with the number of tiles

        Around 50 IP blocks max per minor address
        '''

        # Sort by block offset
        values = sorted(values)

        for refi, (_ref_block_offset, ref_tile_name, ref_block,
                   ref_block_name) in enumerate(values):
            seglets = segtiles.setdefault(ref_tile_name, [])
            ref_as = (
                ref_block["offset"],
                ref_block["offset"] + ref_block["height"] - 1)

            for cmpi in range(refi + 1, len(values)):
                (_cmp_block_offset, cmp_tile_name, cmp_block,
                 cmp_block_name) = values[cmpi]
                cmp_as = (
                    cmp_block["offset"],
                    cmp_block["offset"] + cmp_block["height"] - 1)

                if overlap(ref_as, cmp_as):
                    seglets.append((cmp_tile_name, cmp_block_name))
                # sorting => first non-intersection means no future will intersect
                else:
                    break

    return segtiles


def mk_segments(tiles):
    segments = {}
    segtiles = mk_segtiles(tiles)

    for tile_name, tile in tiles.items():
        for block_name, block in tile['bits'].items():
            segname = mksegment(tile_name, block_name)
            segments[segname] = {
                'tile': tile,
                'tile_name': tile_name,
                'block': block,
                'block_name': block_name,
                'segtiles': segtiles[tile_name],
            }
    return segments


def mksegment(tile_name, block_name):
    '''Create a segment name'''
    return '%s:%s' % (tile_name, block_name)


def tile_segnames(tiles):
    '''Create a list of all (tile_name, block_name) from input tiles'''
    ret = []
    for tile_name, tile in tiles.items():
        if 'bits' not in tile:
            continue

        for block_name in tile['bits'].keys():
            ret.append(mksegment(tile_name, block_name))
    return ret


def load_tiles(db_root):
    # TODO: Migrate to new tilegrid format via library.
    with open("%s/tilegrid.json" % (db_root), "r") as f:
        tiles = json.load(f)
    return tiles


def run(
        db_root,
        bits_file,
        segnames,
        omit_empty_segs=False,
        flag_unknown_bits=False,
        flag_decode_emit=False,
        flag_decode_omit=False,
        verbose=False):
    db = prjxraydb.Database(db_root)
    tiles = load_tiles(db_root)
    segments = mk_segments(tiles)
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
            bitdata,
            flag_decode_emit,
            flag_decode_omit,
            omit_empty_segs,
            segments,
            verbose=verbose)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Decode bits within a tile's address space")

    util.db_root_arg(parser)
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
