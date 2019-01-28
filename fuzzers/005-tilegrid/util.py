#!/usr/bin/env python3

from prjxray import util
'''
Local utils script to hold shared code of the 005-tilegrid fuzzer scripts
'''


def check_frames(tagstr, addrlist):
    frames = set()
    for addrstr in addrlist:
        frame = parse_addr(addrstr, get_base_frame=True)
        frames.add(frame)
    assert len(frames) == 1, ("{}: More than one base address".format(tagstr), map(hex, frames))


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


def propagate_up_INT(grid_x, grid_y, database, tiles_by_grid, wordbase):
    for i in range(50):
        grid_y -= 1
        loc = (grid_x, grid_y)
        if loc not in tiles_by_grid:
            continue

        tile = database[tiles_by_grid[loc]]

        if wordbase == 50:
            wordbase += 1
        else:
            wordbase += 2

        yield tile, wordbase


def add_baseaddr(tile_baseaddrs, tile_name, baseaddr, verbose=False):
    bt = util.addr2btype(baseaddr)
    tile_baseaddr = tile_baseaddrs.setdefault(tile_name, {})
    if bt in tile_baseaddr:
        # actually lets just fail these, better to remove at tcl level to speed up processing
        assert 0, 'duplicate base address'
        assert tile_baseaddr[bt] == [baseaddr, 0]
    else:
        tile_baseaddr[bt] = [baseaddr, 0]
    verbose and print(
        "baseaddr: %s.%s @ %s.0x%08x" %
        (tile["name"], site_name, bt, baseaddr))


def get_entry(tile_type, block_type):
    """
    FIXME: review IOB
        # IOB
        # design_IOB_X0Y100.delta:+bit_00020027_000_29
        # design_IOB_X0Y104.delta:+bit_00020027_008_29
        # design_IOB_X0Y112.delta:+bit_00020027_024_29
        # design_IOB_X0Y120.delta:+bit_00020027_040_29
        # design_IOB_X0Y128.delta:+bit_00020027_057_29
        # design_IOB_X0Y136.delta:+bit_00020027_073_29
        # design_IOB_X0Y144.delta:+bit_00020027_089_29
        # $XRAY_BLOCKWIDTH design_IOB_X0Y100.bit |grep 00020000
        # 0x00020000: 0x2A (42)
        ("RIOI3", "CLB_IO_CLK"): (42, 2, 4),
        ("LIOI3", "CLB_IO_CLK"): (42, 2, 4),
        ("RIOI3_SING", "CLB_IO_CLK"): (42, 2, 4),
        ("LIOI3_SING", "CLB_IO_CLK"): (42, 2, 4),
        ("RIOI3_TBYTESRC", "CLB_IO_CLK"): (42, 2, 4),
        ("LIOI3_TBYTESRC", "CLB_IO_CLK"): (42, 2, 4),
        ("RIOI3_TBYTETERM", "CLB_IO_CLK"): (42, 2, 4),
        ("LIOI3_TBYTETERM", "CLB_IO_CLK"): (42, 2, 4),
        ("LIOB33", "CLB_IO_CLK"): (42, 2, 4),
        ("RIOB33", "CLB_IO_CLK"): (42, 2, 4),
        ("LIOB33", "CLB_IO_CLK"): (42, 2, 4),
        ("RIOB33_SING", "CLB_IO_CLK"): (42, 2, 4),
        ("LIOB33_SING", "CLB_IO_CLK"): (42, 2, 4),
    """
    return {
        # (tile_type, block_type): (frames, words, height)
        ("CLBLL", "CLB_IO_CLK"): (36, 2, 2),
        ("CLBLM", "CLB_IO_CLK"): (36, 2, 2),
        ("HCLK", "CLB_IO_CLK"): (26, 1, 1),
        ("INT", "CLB_IO_CLK"): (28, 2, 2),
        ("BRAM", "CLB_IO_CLK"): (28, 10, None),
        ("BRAM", "BLOCK_RAM"): (128, 10, None),
        ("DSP", "CLB_IO_CLK"): (28, 2, 10),
        ("INT_INTERFACE", "CLB_IO_CLK"): (28, 2, None),
        ("BRAM_INT_INTERFACE", "CLB_IO_CLK"): (28, 2, None),
    }.get((tile_type, block_type), None)


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

    # related to words...
    # deprecated field? Don't worry about for now
    # DSP has some differences between height and words
    block["words"] = words
    if height is None:
        height = words
    block["height"] = height


def get_int_params():
    int_frames = 28
    int_words = 2
    return int_frames, int_words
