#!/usr/bin/env python3

from prjxray import util
import json
import os


# Copied from generate_full.py
def add_tile_bits(
        tile_name,
        tile_db,
        baseaddr,
        offset,
        frames,
        words,
        height=None,
        verbose=False):
    '''
    Record data structure geometry for the given tile baseaddr
    For most tiles there is only one baseaddr, but some like BRAM have multiple
    Notes on multiple block types:
    https://github.com/SymbiFlow/prjxray/issues/145
    '''

    bits = tile_db['bits']
    block_type = util.addr2btype(baseaddr)

    assert offset <= 100, (tile_name, offset)
    # Few rare cases at X=0 for double width tiles split in half
    assert offset >= 0 or "IOB" in tile_name, (tile_name, offset)
    assert 1 <= words <= 101
    assert offset + words <= 101, (
        tile_name, offset + words, offset, words, block_type)

    baseaddr_str = '0x%08X' % baseaddr

    block = bits.get(block_type, None)
    if block is not None:
        verbose and print(
            "%s: existing defintion for %s" % (tile_name, block_type))
        assert block["baseaddr"] == baseaddr_str
        assert block["frames"] == frames
        assert block["offset"] == offset, "%s; orig offset %s, new %s" % (
            tile_name, block["offset"], offset)
        assert block["words"] == words
        return
    block = bits.setdefault(block_type, {})

    # FDRI address
    block["baseaddr"] = baseaddr_str
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


def check_frames(frames):
    baseaddr = set()
    for frame in frames:
        baseaddr.add(frame // 128)
    assert len(baseaddr) == 1, "Multiple base addresses for the same tag"


def load_db(fn):
    for l in open(fn, "r"):
        l = l.strip()
        # FIXME: add offset to name
        # IOB_X0Y101.DFRAME:27.DWORD:3.DBIT:3 00020027_003_03
        parts = l.split(' ')
        tagstr = parts[0]
        addrlist = parts[1:]
        frames = list()
        for addrstr in addrlist:
            frame, wordidx, bitidx = parse_addr(addrstr)
            frames.append(frame)
        check_frames(frames)
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
    tdb_fns = [
        ("iob/build/segbits_tilegrid.tdb", 42, 4),
        # FIXME: height
        ("mmcm/build/segbits_tilegrid.tdb", 30, 101),
        # FIXME: height
        ("pll/build/segbits_tilegrid.tdb", 30, 101),
    ]

    # FIXME: support XADC in ROI
    if os.path.exists("monitor/build/segbits_tilegrid.tdb"):
        # FIXME: height
        tdb_fns.append(("monitor/build/segbits_tilegrid.tdb", 30, 101))
    if os.path.exists("ps7_int/build/segbits_tilegrid.tdb"):
        tdb_fns.append(("ps7_int/build/segbits_tilegrid.tdb", 36, 2))

    for (tdb_fn, frames, words) in tdb_fns:
        for (tile, frame, wordidx) in load_db(tdb_fn):
            tilej = database[tile]
            bitsj = tilej['bits']
            bt = util.addr2btype(frame)
            verbose and print("Add %s %08X_%03u" % (tile, frame, wordidx))
            # Special case for half height IOB
            if tile == "LIOB33_SING_X0Y149":
                tile_words = 2
            else:
                tile_words = words
            add_tile_bits(
                tile,
                tilej,
                frame,
                wordidx,
                frames,
                tile_words,
                verbose=verbose)

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
