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

from prjxray import util
import os
import json
'''
Local utils script to hold shared code of the 005-tilegrid fuzzer scripts
'''


class TileFrames:
    """
    Class for getting the number of frames used for configuring a tile
    with the specified baseaddress using the information from the part's json file
    """

    def __init__(self):
        self.tile_address_to_frames = dict()

    def get_baseaddress(self, region, bus, row, column):
        assert bus == 'BLOCK_RAM' or bus == 'CLB_IO_CLK', 'Incorrect block type'
        address = (row << 17) + (column << 7) + (
            (1 << 22) if region == 'bottom' else 0) + (
                (1 << 23) if bus == 'BLOCK_RAM' else 0)
        return address

    def initialize_address_to_frames(self):
        with open(os.path.join(os.getenv('XRAY_FAMILY_DIR'),
                               os.getenv('XRAY_PART'), 'part.json')) as pf:
            part_json = json.load(pf)
        for clock_region, rows in part_json['global_clock_regions'].items():
            for row, buses in rows['rows'].items():
                for bus, columns in buses['configuration_buses'].items():
                    for column, frames in columns[
                            'configuration_columns'].items():
                        address = self.get_baseaddress(
                            clock_region, bus, int(row), int(column))
                        assert address not in self.tile_address_to_frames
                        self.tile_address_to_frames[address] = frames[
                            'frame_count']

    def get_tile_frames(self, baseaddress):
        if len(self.tile_address_to_frames) == 0:
            self.initialize_address_to_frames()
        assert baseaddress in self.tile_address_to_frames, "Base address not found in the part's json file"
        return self.tile_address_to_frames[baseaddress]


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
        tile_name,
        tile_db,
        baseaddr,
        offset,
        frames,
        words,
        tile_frames,
        verbose=False):
    '''
    Record data structure geometry for the given tile baseaddr
    For most tiles there is only one baseaddr, but some like BRAM have multiple
    Notes on multiple block types:
    https://github.com/SymbiFlow/prjxray/issues/145
    '''
    bits = tile_db['bits']
    block_type = util.addr2btype(baseaddr)

    # Extract the information about the maximal number of frames from the part's json
    max_frames = tile_frames.get_tile_frames(baseaddr)
    if frames > max_frames:
        print(
            "Warning: The number of frames for base address {} specified for the tile {} ({}) exceeds the maximum allowed value ({}). Falling back to the maximum value."
            .format(hex(baseaddr), tile_name, frames, max_frames))
        frames = max_frames
    # If frames count is None then use the maximum
    if frames is None:
        frames = max_frames

    assert offset <= 100, (tile_name, offset)
    # Few rare cases at X=0 for double width tiles split in half => small negative offset
    assert offset >= 0 or "IOB" in tile_name or "GTX_INT_INTERFACE" in tile_name, (
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
