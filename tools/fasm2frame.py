#!/usr/bin/env python3

import os
import re
import sys
import json

# Based on segprint function
# Modified to return dict instead of list
segbitsdb = dict()


def get_database(segtype):
    if segtype in segbitsdb:
        return segbitsdb[segtype]

    segbitsdb[segtype] = {}

    with open("%s/%s/segbits_%s.db" % (os.getenv("XRAY_DATABASE_DIR"),
                                       os.getenv("XRAY_DATABASE"), segtype),
              "r") as f:
        for line in f:
            # CLBLM_L.SLICEL_X1.ALUT.INIT[10] 29_14
            parts = line.split()
            name = parts[0]
            vals = parts[1:]
            segbitsdb[segtype][name] = vals

    with open("%s/%s/segbits_int_%s.db" %
              (os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"),
               segtype[-1]), "r") as f:
        for line in f:
            # CLBLM_L.SLICEL_X1.ALUT.INIT[10] 29_14
            parts = line.split()
            name = parts[0]
            vals = parts[1:]
            segbitsdb[segtype][name] = vals

    return segbitsdb[segtype]


def dump_frames_verbose(frames):
    print()
    print("Frames: %d" % len(frames))
    for addr in sorted(frames.keys()):
        words = frames[addr]
        print(
            '0x%08X ' % addr + ', '.join(['0x%08X' % w
                                          for w in words]) + '...')


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


def run(f_in, f_out, sparse=False, debug=False):
    # address to array of 101 32 bit words
    frames = {}

    def frames_init():
        '''Set all frames to 0'''
        for segj in grid['segments'].values():
            seg_baseaddr, seg_word_base = segj['baseaddr']
            seg_baseaddr = int(seg_baseaddr, 0)
            for coli in range(segj['frames']):
                frame_init(seg_baseaddr + coli)

    def frame_init(addr):
        '''Set given frame to 0'''
        if not addr in frames:
            frames[addr] = [0 for _i in range(101)]

    def frame_set(frame_addr, word_addr, bit_index):
        '''Set given bit in given frame address and word'''
        frames[frame_addr][word_addr] |= 1 << bit_index

    with open("%s/%s/tilegrid.json" % (os.getenv("XRAY_DATABASE_DIR"),
                                       os.getenv("XRAY_DATABASE")), "r") as f:
        grid = json.load(f)

    if not sparse:
        # Initiaize bitstream to 0
        frames_init()

    for l in f_in:
        # Comment
        # Remove all text including and after #
        i = l.rfind('#')
        if i >= 0:
            l = l[0:i]
        l = l.strip()

        # Ignore blank lines
        if not l:
            continue

        # tile.site.stuff value
        # INT_L_X10Y102.CENTER_INTER_L.IMUX_L1 EE2END0
        m = re.match(
            r'([a-zA-Z0-9_]+)[.]([a-zA-Z0-9_]+)[.]([a-zA-Z0-9_.\[\]]+)[ ](.+)',
            l)
        if not m:
            raise Exception("Bad line: %s" % l)
        tile = m.group(1)
        site = m.group(2)
        suffix = m.group(3)
        value = m.group(4)

        tilej = grid['tiles'][tile]
        seg = tilej['segment']
        segj = grid['segments'][seg]
        seg_baseaddr, seg_word_base = segj['baseaddr']
        seg_baseaddr = int(seg_baseaddr, 0)

        # Ensure that all frames exist for this segment
        # FIXME: type dependent
        for coli in range(segj['frames']):
            frame_init(seg_baseaddr + coli)

        # Now lets look up the bits we need frames for
        segdb = get_database(segj['type'])

        def clb2dbkey(tile, tilej, site, suffix, value):
            def slice_global2x01(tile_name, tile_type, site):
                # SLICE_X12Y102 => SLICEL_X0
                m = re.match(r'SLICE_X([0-9]+)Y[0-9]+', site)
                xg = int(m.group(1))

                prefix = {
                    'CLBLL_L': {
                        0: 'SLICEL',
                        1: 'SLICEL'
                    },
                    'CLBLM_L': {
                        0: 'SLICEM',
                        1: 'SLICEL'
                    },
                    'CLBLL_R': {
                        0: 'SLICEL',
                        1: 'SLICEL'
                    },
                    'CLBLM_R': {
                        0: 'SLICEM',
                        1: 'SLICEL'
                    },
                }
                x01 = xg % 2
                return '%s_X%d' % (prefix[tile_type][x01], x01)

            db_site = slice_global2x01(tile, tilej['type'], site)
            db_k = '%s.%s.%s' % (tilej['type'], db_site, suffix)
            return db_k

        def int2dbkey(tile, tilej, site, suffix, value):
            return '%s.%s.%s' % (tilej['type'], suffix, value)

        tile2dbkey = {
            'CLBLL_L': clb2dbkey,
            'CLBLL_R': clb2dbkey,
            'CLBLM_L': clb2dbkey,
            'CLBLM_R': clb2dbkey,
            'INT_L': int2dbkey,
            'INT_R': int2dbkey,
            'HCLK_L': int2dbkey,
            'HCLK_R': int2dbkey,
        }

        f = tile2dbkey.get(tilej['type'], None)
        if f is None:
            raise Exception("Unhandled segment type %s" % tilej['type'])
        db_k = f(tile, tilej, site, suffix, value)

        try:
            db_vals = segdb[db_k]
        except KeyError:
            raise Exception(
                "Key %s (from line '%s') not found in segment DB %s" %
                (db_k, l, segj['type']))

        for val in db_vals:
            # Default is 0. Skip explicit call outs
            if val[0] == '!':
                continue
            # 28_05 => 28, 05
            seg_word_column, word_bit_n = val.split('_')
            seg_word_column, word_bit_n = int(seg_word_column), int(word_bit_n)
            # Now we have the word column and word bit index
            # Combine with the segments relative frame position to fully get the position
            frame_addr = seg_baseaddr + seg_word_column
            # 2 words per segment
            word_addr = seg_word_base + word_bit_n // 32
            bit_index = word_bit_n % 32
            frame_set(frame_addr, word_addr, bit_index)

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
