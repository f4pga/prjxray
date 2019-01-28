#!/usr/bin/env python3

from __future__ import print_function
from prjxray import util
'''
Local utils script to hold shared code of the 005-tilegrid fuzzer scripts
'''


def get_entry(tile_type, block_type):
    """ Get frames and words for a given tile_type (e.g. CLBLL) and block_type (CLB_IO_CLK, BLOCK_RAM, etc). """
    return {
        # (tile_type, block_type): (frames, words, height)
        ("CLBLL", "CLB_IO_CLK"): (36, 2, None),
        ("CLBLM", "CLB_IO_CLK"): (36, 2, None),
        ("HCLK", "CLB_IO_CLK"): (26, 1, None),
        ("INT", "CLB_IO_CLK"): (28, 2, None),
        ("BRAM", "CLB_IO_CLK"): (28, 10, None),
        ("BRAM", "BLOCK_RAM"): (128, 10, None),
        ("DSP", "CLB_IO_CLK"): (28, 2, None),
    }.get((tile_type, block_type), None)


def get_int_params():
    int_frames, int_words, _ = get_entry('INT', 'CLB_IO_CLK')
    return int_frames, int_words


def add_tile_bits(
        tile_name, tile_db, baseaddr, offset, frames, words, verbose=False):
    '''
    Record data structure geometry for the given tile baseaddr
    For most tiles there is only one baseaddr, but some like BRAM have multiple
    Notes on multiple block types:
    https://github.com/SymbiFlow/prjxray/issues/145
    '''
    bits = tile_db['bits']
    block_type = util.addr2btype(baseaddr)

    assert offset <= 100, (tile_name, offset)
    # Few rare cases at X=0 for double width tiles split in half => small negative offset
    assert offset >= 0 or "IOB" in tile_name, (
        tile_name, hex(baseaddr), offset)
    assert 1 <= words <= 101, words
    assert offset + words <= 101, (
        tile_name, offset + words, offset, words, block_type)

    baseaddr_str = '0x%08X' % baseaddr
    block = bits.get(block_type, None)
    if block is not None:
        verbose and print(
            "%s: existing defintion for %s" % (tile_name, block_type))
        assert block["baseaddr"] == baseaddr_str
        assert block["frames"] == frames, (block, frames)
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

    # Number of words used by tile.
    block["words"] = words
