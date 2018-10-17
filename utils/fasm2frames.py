#!/usr/bin/env python3

import os
import re
import sys
import json
import collections


class FASMSyntaxError(Exception):
    pass


def parsebit(val):
    '''Return "!012_23" => (12, 23, False)'''
    isset = True
    # Default is 0. Skip explicit call outs
    if val[0] == '!':
        isset = False
        val = val[1:]
    # 28_05 => 28, 05
    seg_word_column, word_bit_n = val.split('_')
    return int(seg_word_column), int(word_bit_n), isset


# TODO: migrate to library
def process_db(tile_type, process):
    fns = [
        # sites
        "%s/%s/segbits_%s.db" % (
            os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"),
            tile_type.lower()),
        # interconnect
        "%s/%s/segbits_int_%s.db" % (
            os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"),
            tile_type[-1].lower()),
    ]

    for fn in fns:
        if os.path.exists(fn):
            with open(fn, "r") as f:
                for line in f:
                    process(line)


'''
Loosely based on segprint function
Maybe better to return as two distinct dictionaries?

{
    'tile.meh': {
            'O5': [(11, 2, False), (12, 2, True)],
            'O6': [(11, 2, True), (12, 2, False)],
    },
}
'''
segbitsdb = dict()


def get_database(tile_type):
    if tile_type in segbitsdb:
        return segbitsdb[tile_type]

    segbitsdb[tile_type] = {}

    def process(l):
        # CLBLM_L.SLICEL_X1.ALUT.INIT[10] 29_14
        parts = l.strip().split()
        name = parts[0]
        bit_vals = parts[1:]

        # Assumption
        # only 1 bit => non-enumerated value
        if len(bit_vals) == 1:
            seg_word_column, word_bit_n, isset = parsebit(bit_vals[0])
            if not isset:
                raise Exception(
                    "Expect single bit DB entries to be set, got %s" % l)
            # Treat like an enumerated value with keys 0 or 1
            assert name not in segbitsdb[tile_type]
            segbitsdb[tile_type][name] = {
                '0': [(seg_word_column, word_bit_n, 0)],
                '1': [(seg_word_column, word_bit_n, 1)],
            }
        else:
            # An enumerated value
            # Split the base name and selected key
            m = re.match(r'(.+)[.](.+)', name)
            namepart = m.group(1)
            key = m.group(2)

            # May or may not be the first key encountered
            bits_map = segbitsdb[tile_type].setdefault(namepart, {})
            bits_map[key] = [parsebit(x) for x in bit_vals]

    process_db(tile_type, process)

    return segbitsdb[tile_type]


def dump_frames_verbose(frames):
    print()
    print("Frames: %d" % len(frames))
    for addr in sorted(frames.keys()):
        words = frames[addr]
        print(
            '0x%08X ' % addr + ', '.join(['0x%08X' % w for w in words]) +
            '...')


def dump_frames_sparse(frames):
    print()
    print("Frames: %d" % len(frames))
    for addr in sorted(frames.keys()):
        words = frames[addr]

        # Skip frames without filled words
        for w in words:
            if w:
                break
        else:
            continue

        print('Frame @ 0x%08X' % addr)
        for i, w in enumerate(words):
            if w:
                print('  % 3d: 0x%08X' % (i, w))


def dump_frm(f, frames):
    '''Write a .frm file given a list of frames, each containing a list of 101 32 bit words'''
    for addr in sorted(frames.keys()):
        words = frames[addr]
        f.write(
            '0x%08X ' % addr + ','.join(['0x%08X' % w for w in words]) + '\n')


def mksegment(tile_name, block_name):
    '''Create a segment name'''
    return '%s:%s' % (tile_name, block_name)


def mk_grid():
    '''Load tilegrid, flattening all blocks into one dictionary'''

    with open("%s/%s/tilegrid.json" % (os.getenv("XRAY_DATABASE_DIR"),
                                       os.getenv("XRAY_DATABASE")), "r") as f:
        new_grid = json.load(f)

    # TODO: Migrate to new tilegrid format via library.
    grid = {'tiles': new_grid, 'segments': {}}

    for tile_name, tile in grid['tiles'].items():
        for block_name, block in tile['bits'].items():
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


def frame_init(frames, addr):
    '''Set given frame to 0'''
    if not addr in frames:
        frames[addr] = [0 for _i in range(101)]


def frames_init(frames, grid):
    '''Set all frames to 0'''
    for segj in grid['segments'].values():
        seg_baseaddr, seg_word_base = segj['baseaddr']
        seg_baseaddr = int(seg_baseaddr, 0)
        for coli in range(segj['frames']):
            frame_init(frames, seg_baseaddr + coli)


def frame_set(frames, frame_addr, word_addr, bit_index):
    '''Set given bit in given frame address and word'''
    frames[frame_addr][word_addr] |= 1 << bit_index


def frame_clear(frames, frame_addr, word_addr, bit_index):
    '''Set given bit in given frame address and word'''
    frames[frame_addr][word_addr] &= 0xFFFFFFFF ^ (1 << bit_index)


def parse_line(l):
    # Comment
    # Remove all text including and after #
    i = l.rfind('#')
    if i >= 0:
        l = l[0:i]
    l = l.strip()

    # Ignore blank lines
    if not l:
        return

    # tile.site.stuff value
    # INT_L_X10Y102.CENTER_INTER_L.IMUX_L1 EE2END0
    # Optional value
    m = re.match(r'([a-zA-Z0-9_]+)[.]([a-zA-Z0-9_.\[\]]+)([ ](.+))?', l)
    if not m:
        raise FASMSyntaxError("Bad line: %s" % l)
    tile = m.group(1)
    name = m.group(2)
    value = m.group(4)

    return tile, name, value


def check_duplicate(used_names, tile, name, l, line_number):
    '''Throw an exception if a conflicting FASM directive was given'''
    used_name = (tile, name)
    old_line_number = used_names.get(used_name, None)
    if old_line_number:
        raise FASMSyntaxError(
            "Duplicate name lines %d and %d, second line: %s" %
            (old_line_number, line_number, l))
    used_names[used_name] = line_number


def update_segbit(
        frames, seg_word_column, word_bit_n, isset, seg_baseaddr,
        seg_word_base):
    '''Set  or clear a single bit in a segment at the given word column and word bit position'''
    # Now we have the word column and word bit index
    # Combine with the segments relative frame position to fully get the position
    frame_addr = seg_baseaddr + seg_word_column
    # 2 words per segment
    word_addr = seg_word_base + word_bit_n // 32
    bit_index = word_bit_n % 32
    if isset:
        frame_set(frames, frame_addr, word_addr, bit_index)
    else:
        frame_clear(frames, frame_addr, word_addr, bit_index)


def default_value(db_vals, name):
    # If its binary, allow omitted value default to 1
    if tuple(sorted(db_vals.keys())) == ('0', '1'):
        return '1'
    else:
        raise FASMSyntaxError(
            "Enumerable entry %s must have explicit value" % name)


def process_line(line_number, l, grid, frames, used_names):
    parsed = parse_line(l)
    # empty line
    if not parsed:
        return
    tile_name, name, value = parsed
    check_duplicate(used_names, tile_name, name, l, line_number)

    tilej = grid['tiles'][tile_name]
    for block_name, block in tilej['bits'].items():
        segname = mksegment(tile_name, block_name)

        segj = grid['segments'][segname]
        seg_baseaddr, seg_word_base = segj['baseaddr']
        seg_baseaddr = int(seg_baseaddr, 0)

        # Ensure that all frames exist for this segment
        # FIXME: type dependent
        for coli in range(segj['frames']):
            frame_init(frames, seg_baseaddr + coli)

        # Now lets look up the bits we need frames for
        segdb = get_database(segj['type'])

        db_k = '%s.%s' % (tilej['type'], name)
        try:
            db_vals = segdb[db_k]
        except KeyError:
            raise FASMSyntaxError(
                "Segment DB %s, key %s not found from line '%s'" %
                (segj['type'], db_k, l)) from None

        if not value:
            value = default_value(db_vals, name)

        # Get the specific entry we need
        try:
            db_vals = db_vals[value]
        except KeyError:
            raise FASMSyntaxError(
                "Invalid entry %s. Valid entries are %s" %
                (value, db_vals.keys()))

        for seg_word_column, word_bit_n, isset in db_vals:
            update_segbit(
                frames, seg_word_column, word_bit_n, isset, seg_baseaddr,
                seg_word_base)


def run(f_in, f_out, sparse=False, debug=False):
    # address to array of 101 32 bit words
    frames = {}
    # Directives we've seen so far
    # Complain if there is a duplicate
    # Contains line number of last entry
    used_names = {}

    grid = mk_grid()

    if not sparse:
        # Initiaize bitstream to 0
        frames_init(frames, grid)

    for line_number, l in enumerate(f_in, 1):
        process_line(line_number, l, grid, frames, used_names)

    if debug:
        #dump_frames_verbose(frames)
        dump_frames_sparse(frames)

    dump_frm(f_out, frames)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Convert FPGA configuration description ("FPGA assembly") into binary frame equivalent'
    )

    parser.add_argument(
        '--sparse', action='store_true', help="Don't zero fill all frames")
    parser.add_argument(
        '--debug', action='store_true', help="Print debug dump")
    parser.add_argument(
        'fn_in',
        default='/dev/stdin',
        nargs='?',
        help='Input FPGA assembly (.fasm) file')
    parser.add_argument(
        'fn_out',
        default='/dev/stdout',
        nargs='?',
        help='Output FPGA frame (.frm) file')

    args = parser.parse_args()
    run(
        open(args.fn_in, 'r'),
        open(args.fn_out, 'w'),
        sparse=args.sparse,
        debug=args.debug)
