#!/usr/bin/env python3

from prjxray import util
import json


# Copied from generate_full.py
def add_tile_bits(tile_db, baseaddr, offset, frames, words, height=None):
    '''
    Record data structure geometry for the given tile baseaddr
    For most tiles there is only one baseaddr, but some like BRAM have multiple
    Notes on multiple block types:
    https://github.com/SymbiFlow/prjxray/issues/145
    '''

    bits = tile_db['bits']
    block_type = util.addr2btype(baseaddr)

    assert 0 <= offset <= 100, offset
    assert 1 <= words <= 101
    assert offset + words <= 101, (
        tile_db, offset + words, offset, words, block_type)

    assert block_type not in bits
    block = bits.setdefault(block_type, {})

    # FDRI address
    block["baseaddr"] = '0x%08X' % baseaddr
    # Number of frames this entry is sretched across
    # that is the following FDRI addresses are used: range(baseaddr, baseaddr + frames)
    block["frames"] = frames

    # Index of first word used within each frame
    block["offset"] = offset

    # related to words...
    # deprecated field? Don't worry about for now
    # DSP has some differences between height and words
    block["words"] = words
    if height is None:
        height = words
    block["height"] = height


def parse_addr(line):
    # 00020027_003_03
    line = line.split("_")
    frame = int(line[0], 16)
    wordidx = int(line[1], 10)
    bitidx = int(line[2], 10)
    return frame, wordidx, bitidx


def load_db(fn):
    for l in open(fn, "r"):
        l = l.strip()
        # FIXME: add offset to name
        # IOB_X0Y101.DFRAME:27.DWORD:3.DBIT:3 00020027_003_03
        parts = l.split(' ')
        assert len(parts) == 2, "Unresolved bit: %s" % l
        tagstr, addrstr = parts

        frame, wordidx, bitidx = parse_addr(addrstr)
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
    tdb_fns = [
        ("iob/build/segbits_tilegrid.tdb", 42, 4),
        # FIXME: height
        ("mmcm/build/segbits_tilegrid.tdb", 30, 4),
    ]
    for (tdb_fn, frames, words) in tdb_fns:
        for (tile, frame, wordidx) in load_db(tdb_fn):
            tilej = database[tile]
            bitsj = tilej['bits']
            bt = util.addr2btype(frame)
            verbose and print("Add %s %08X_%03u" % (tile, frame, wordidx))
            add_tile_bits(tilej, frame, wordidx, frames, words)

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
