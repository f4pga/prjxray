#!/usr/bin/env python3

from __future__ import print_function
import json
import util as localutil


def load_db(fn):
    for l in open(fn, "r"):
        l = l.strip()
        # FIXME: add offset to name
        # IOB_X0Y101.DFRAME:27.DWORD:3.DBIT:3 00020027_003_03
        parts = l.split(' ')
        tagstr = parts[0]
        addrlist = parts[1:]
        localutil.check_frames(addrlist)
        # Take the first address in the list
        frame, wordidx, bitidx = localutil.parse_addr(addrlist[0])

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
    int_frames, int_words, _ = localutil.get_entry('INT', 'CLB_IO_CLK')
    tdb_fns = [
        ("iob/build/segbits_tilegrid.tdb", 42, 4),
        # FIXME: height
        ("mmcm/build/segbits_tilegrid.tdb", 30, 101),
        # FIXME: height
        ("pll/build/segbits_tilegrid.tdb", 30, 101),
        ("monitor/build/segbits_tilegrid.tdb", 30, 101),
        ("bram/build/segbits_tilegrid.tdb", 28, 10),
        ("bram_block/build/segbits_tilegrid.tdb", 128, 10),
        ("clb/build/segbits_tilegrid.tdb", 36, 2),
        ("dsp/build/segbits_tilegrid.tdb", 28, 2),
        ("clb_int/build/segbits_tilegrid.tdb", int_frames, int_words),
        ("iob_int/build/segbits_tilegrid.tdb", int_frames, int_words),
        ("bram_int/build/segbits_tilegrid.tdb", int_frames, int_words),
        ("dsp_int/build/segbits_tilegrid.tdb", int_frames, int_words),
    ]

    for (tdb_fn, frames, words) in tdb_fns:
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
