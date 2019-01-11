#!/usr/bin/env python3

from prjxray import util
'''
Local utils script to hold shared code of the 005-tilegrid fuzzer scripts
'''

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
    # Few rare cases at X=0 for double width tiles split in half => small negative offset
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
