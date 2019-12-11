#!/usr/bin/env python3

import json
import util as localutil
import os.path

ZERO_CANDIDATES = '<0 candidates>'


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

        # Skip <0 candidates> frames. This happens with unbounded IOBs
        if ZERO_CANDIDATES in l:
            continue

        parts = l.split(' ')
        tagstr = parts[0]
        addrlist = parts[1:]
        check_frames(tagstr, addrlist)
        # Take the first address in the list
        frame, wordidx, bitidx = parse_addr(addrlist[0])

        bitidx_up = False

        tparts = tagstr.split('.')
        tile = tparts[0]
        for part in tparts[1:]:
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
        ("iob/build/segbits_tilegrid.tdb", 42, 4),
        ("ioi/build/segbits_tilegrid.tdb", 42, 4),
        ("mmcm/build/segbits_tilegrid.tdb", 30, 101),
        ("pll/build/segbits_tilegrid.tdb", 30, 26),
        ("monitor/build/segbits_tilegrid.tdb", 30, 101),
        ("bram/build/segbits_tilegrid.tdb", 28, 10),
        ("bram_block/build/segbits_tilegrid.tdb", 128, 10),
        ("clb/build/segbits_tilegrid.tdb", 36, 2),
        ("cfg/build/segbits_tilegrid.tdb", 30, 101),
        ("dsp/build/segbits_tilegrid.tdb", 28, 10),
        ("clk_hrow/build/segbits_tilegrid.tdb", 30, 18),
        ("clk_bufg/build/segbits_tilegrid.tdb", 30, 8),
        ("hclk_cmt/build/segbits_tilegrid.tdb", 30, 10),
        ("hclk_ioi/build/segbits_tilegrid.tdb", 42, 1),
        ("clb_int/build/segbits_tilegrid.tdb", int_frames, int_words),
        ("iob_int/build/segbits_tilegrid.tdb", int_frames, int_words),
        ("bram_int/build/segbits_tilegrid.tdb", int_frames, int_words),
        ("dsp_int/build/segbits_tilegrid.tdb", int_frames, int_words),
        ("fifo_int/build/segbits_tilegrid.tdb", int_frames, int_words),
        ("ps7_int/build/segbits_tilegrid.tdb", int_frames, int_words),
        ("cfg_int/build/segbits_tilegrid.tdb", int_frames, int_words),
        ("monitor_int/build/segbits_tilegrid.tdb", int_frames, int_words),
        (
            "orphan_int_column/build/segbits_tilegrid.tdb", int_frames,
            int_words),
    ]

    for (tdb_fn, frames, words) in tdb_fns:
        if not os.path.exists(tdb_fn):
            verbose and print('Skipping {}, file not found!'.format(tdb_fn))
            continue

        for (tile, frame, wordidx) in load_db(tdb_fn):
            tilej = database[tile]
            verbose and print("Add %s %08X_%03u" % (tile, frame, wordidx))
            localutil.add_tile_bits(tile, tilej, frame, wordidx, frames, words)

    # Save
    json.dump(
        database,
        open(fn_out, "w"),
        sort_keys=True,
        indent=4,
        separators=(",", ": "))


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
