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
from collections import namedtuple
from prjxray import bitstream
from prjxray.grid_types import BlockType
from prjxray.util import OpenSafeFile
import enum


class PsuedoPipType(enum.Enum):
    ALWAYS = 'always'
    DEFAULT = 'default'
    HINT = 'hint'


def read_ppips(f):
    ppips = {}

    for l in f:
        l = l.strip()
        if not l:
            continue

        feature, ppip_type = l.split(' ')

        ppips[feature] = PsuedoPipType(ppip_type)

    return ppips


Bit = namedtuple('Bit', 'word_column word_bit isset')


def parsebit(val):
    '''Return "!012_23" => (12, 23, False)'''
    isset = True
    # Default is 0. Skip explicit call outs
    if val[0] == '!':
        isset = False
        val = val[1:]
    # 28_05 => 28, 05
    parts = val.split('_')
    assert len(parts) == 2, val
    seg_word_column, word_bit_n = parts

    return Bit(
        word_column=int(seg_word_column),
        word_bit=int(word_bit_n),
        isset=isset,
    )


def read_segbits(f):
    segbits = {}

    for l in f:
        # CLBLM_L.SLICEL_X1.ALUT.INIT[10] 29_14
        l = l.strip()

        if not l:
            continue

        parts = l.split(' ')

        assert len(parts) > 1, l

        segbits[parts[0]] = [parsebit(val) for val in parts[1:]]

    return segbits


class TileSegbits(object):
    def __init__(self, tile_db):
        self.segbits = {}
        self.ppips = {}
        self.feature_addresses = {}

        if tile_db.ppips is not None:
            with OpenSafeFile(tile_db.ppips) as f:
                self.ppips = read_ppips(f)

        if tile_db.segbits is not None:
            with OpenSafeFile(tile_db.segbits) as f:
                self.segbits[BlockType.CLB_IO_CLK] = read_segbits(f)

        if tile_db.block_ram_segbits is not None:
            with OpenSafeFile(tile_db.block_ram_segbits) as f:
                self.segbits[BlockType.BLOCK_RAM] = read_segbits(f)

        for block_type in self.segbits:
            for feature in self.segbits[block_type]:
                sidx = feature.rfind('[')
                eidx = feature.rfind(']')

                if sidx != -1:
                    assert eidx != -1

                    base_feature = feature[:sidx]

                    if base_feature not in self.feature_addresses:
                        self.feature_addresses[base_feature] = {}

                    self.feature_addresses[base_feature][int(
                        feature[sidx + 1:eidx])] = (block_type, feature)

    def match_bitdata(self, block_type, bits, bitdata, match_filter=None):
        """ Return matching features for tile bits data (grid.Bits) and bitdata.

        See bitstream.load_bitdata for details on bitdata structure.

        """

        if block_type not in self.segbits:
            return

        for feature, segbit in self.segbits[block_type].items():
            match = True
            skip = False
            for query_bit in segbit:
                if match_filter is not None and not match_filter(block_type,
                                                                 query_bit):
                    skip = True
                    break

                frame = bits.base_address + query_bit.word_column
                bitidx = bits.offset * bitstream.WORD_SIZE_BITS + query_bit.word_bit

                if frame not in bitdata:
                    match = not query_bit.isset
                    if match:
                        continue
                    else:
                        break

                found_bit = bitidx in bitdata[frame][1]
                match = found_bit == query_bit.isset

                if not match:
                    break

            if not match or skip:
                continue

            def inner():
                for query_bit in segbit:
                    if query_bit.isset:
                        frame = bits.base_address + query_bit.word_column
                        bitidx = bits.offset * bitstream.WORD_SIZE_BITS + query_bit.word_bit
                        yield (frame, bitidx)

            yield (tuple(inner()), feature)

    def map_bit_to_frame(self, block_type, bits, bit):
        """ Convert bit from segbit to frame data. """
        return Bit(
            word_column=bits.base_address + bit.word_column,
            word_bit=bits.offset * bitstream.WORD_SIZE_BITS + bit.word_bit,
            isset=bit.isset,
        )

    def feature_to_bits(self, bits_map, feature, address=0):
        if feature in self.ppips:
            return

        for block_type in self.segbits:
            if address == 0 and feature in self.segbits[block_type]:
                for bit in self.segbits[block_type][feature]:
                    yield block_type, self.map_bit_to_frame(
                        block_type, bits_map[block_type], bit)
                return

        block_type, feature = self.feature_addresses[feature][address]
        for bit in self.segbits[block_type][feature]:
            yield block_type, self.map_bit_to_frame(
                block_type, bits_map[block_type], bit)
