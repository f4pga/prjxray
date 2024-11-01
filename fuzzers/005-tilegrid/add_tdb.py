#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

from prjxray import xjson
import json
import util as localutil
import os.path


def check_frames(tagstr, addrlist):
    frames = set()
    for addrstr in addrlist:
        frame = parse_addr(addrstr, get_base_frame=True)
        frames.add(frame)
    assert len(frames) == 1, (
        "{}: More than one base address".format(tagstr), map(hex, frames))


def parse_addr(line, only_frame=False, get_base_frame=False):
    # 00020027_003_03
    line = line.split("_")
    frame = int(line[0], 16)
    wordidx = int(line[1], 10)
    bitidx = int(line[2], 10)

    if get_base_frame:
        delta = frame % 128
        frame -= delta
        return frame

    return frame, wordidx, bitidx


def load_db(fn):
    for l in open(fn, "r"):
        l = l.strip()
        # FIXME: add offset to name
        # IOB_X0Y101.DFRAME:27.DWORD:3.DBIT:3 00020027_003_03
        parts = l.split(' ')
        tagstr = parts[0]
        addrlist = parts[1:]
        assert not any(s == '<const0>' for s in addrlist), (fn, l)
        check_frames(tagstr, addrlist)
        # Take the first address in the list
        frame, wordidx, bitidx = parse_addr(addrlist[0])

        bitidx_up = False

        tparts = tagstr.split('.')
        tile = tparts[0]

        for part in tparts[1:]:
            # Auto align the frame address to the next lowest multiple of 0x80.
            if part == 'AUTO_FRAME':
                frame -= (frame % 0x80)
                continue

            k, v = part.split(':')
            if k == "DFRAME":
                frame -= int(v, 16)
            elif k == "DWORD":
                wordidx -= int(v, 10)
            elif k == "DBIT":
                bitidx -= int(v, 10)
                bitidx_up = True
            else:
                assert 0, (l, part)

        # XXX: maybe just ignore bitidx and always set to 0 instead of allowing explicit
        # or detect the first delta auto and assert they are all the same
        if not bitidx_up:
            bitidx = 0
        assert bitidx == 0, l
        assert frame % 0x80 == 0, "Unaligned frame at 0x%08X" % frame
        yield (tile, frame, wordidx)


def run(fn_in, fn_out, verbose=False):
    database = json.load(open(fn_in, "r"))

    # Load a map of sites to base addresses
    # Need to figure out the
    # FIXME: generate frames from part file (or equivilent)
    # See https://github.com/SymbiFlow/prjxray/issues/327
    # FIXME: generate words from pitch
    int_frames, int_words = localutil.get_int_params()
    tdb_fns = [
        ("iob", 42, 4),
        ("iob18", 42, 4),
        ("ioi", 42, 4),
        ("ioi18", 42, 4),
        ("mmcm", 30, 49),
        ("pll", 30, 27),
        ("monitor", 30, 101),
        ("bram", 28, 10),
        ("bram_block", 128, 10),
        ("clb", 36, 2),
        ("cfg", 30, 101),
        ("dsp", 28, 10),
        ("clk_hrow", 30, 18),
        ("clk_bufg", 30, 8),
        ("hclk_cmt", 30, 10),
        ("hclk_ioi", 42, 1),
        ("pcie", 36, 101),
        ("gtp_common", 32, 101),
        ("gtp_channel", 32, 22),
        ("gtx_common", 32, 101),
        ("gtx_channel", 32, 22),
        ("clb_int", int_frames, int_words),
        ("iob_int", int_frames, int_words),
        ("iob18_int", int_frames, int_words),
        ("bram_int", int_frames, int_words),
        ("dsp_int", int_frames, int_words),
        ("fifo_int", int_frames, int_words),
        ("ps7_int", int_frames, int_words),
        ("cfg_int", int_frames, int_words),
        ("monitor_int", int_frames, int_words),
        ("orphan_int_column", int_frames, int_words),
        ("gtp_int_interface", int_frames, int_words),
        ("gtx_int_interface", int_frames, int_words),
        ("pcie_int_interface", int_frames, int_words),
    ]

    tile_frames_map = localutil.TileFrames()
    for (subdir, frames, words) in tdb_fns:
        tdb_fn = os.path.join(
            subdir, 'build_{}'.format(os.environ['XRAY_PART']),
            'segbits_tilegrid.tdb')
        if not os.path.exists(tdb_fn):
            verbose and print('Skipping {}, file not found!'.format(tdb_fn))
            continue

        for (tile, frame, wordidx) in load_db(tdb_fn):
            tilej = database[tile]
            verbose and print("Add %s %08X_%03u" % (tile, frame, wordidx))
            localutil.add_tile_bits(
                tile, tilej, frame, wordidx, frames, words, tile_frames_map)

    # Save
    xjson.pprint(open(fn_out, "w"), database)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Annotate tilegrid addresses using solved base addresses")
    parser.add_argument("--verbose", action="store_true", help="")
    parser.add_argument("--fn-in", required=True, help="")
    parser.add_argument("--fn-out", required=True, help="")
    args = parser.parse_args()

    run(args.fn_in, args.fn_out, verbose=args.verbose)


if __name__ == "__main__":
    main()
