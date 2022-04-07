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
""" TileSegbitsAlias provides an alias from one tile type to another.
TileSegbitsAlias performs severals functions to achieve the alias:
 - Remaps tile type from the original tile type to the alias tile type
 - Offsets the bits from the original to the alias type
 - Renames sites from the original to the alias type
 - Filters bits outside of the alias.


"""

from prjxray import bitstream
from prjxray.grid_types import Bits
from prjxray.tile_segbits import read_ppips
from prjxray.util import OpenSafeFile


class TileSegbitsAlias(object):
    def __init__(self, db, tile_type, bits_map):
        # Name of tile_type that is using the alias
        self.tile_type = tile_type

        # Name of aliased tile_type
        self.alias_tile_type = None

        # BlockType -> BitAlias map
        self.alias = {}

        self.bits_map = bits_map

        # BlockType -> aliased Bits map
        self.alias_bits_map = {}

        # aliased site name to site name map
        self.sites_rev_map = {}

        for block_type in bits_map:
            self.alias[block_type] = bits_map[block_type].alias
            self.alias_bits_map[block_type] = Bits(
                base_address=bits_map[block_type].base_address,
                frames=bits_map[block_type].frames,
                offset=bits_map[block_type].offset -
                self.alias[block_type].start_offset,
                words=bits_map[block_type].words,
                alias=None,
            )

            if self.alias_tile_type is None:
                self.alias_tile_type = self.alias[block_type].tile_type
            else:
                assert self.alias_tile_type == self.alias[block_type].tile_type

            self.sites_rev_map[block_type] = {}
            for site, alias_site in self.alias[block_type].sites.items():
                assert alias_site not in self.sites_rev_map[block_type]
                self.sites_rev_map[block_type][alias_site] = site

        tile_db = db.tile_types[self.tile_type]
        self.ppips = {}

        if tile_db.ppips is not None:
            with OpenSafeFile(tile_db.ppips) as f:
                self.ppips = read_ppips(f)
        self.tile_segbits = db.get_tile_segbits(self.alias_tile_type)

    def map_feature_to_segbits(self, feature):
        """ Map from the output feature name to the aliased feature name. """
        parts = feature.split('.')

        assert parts[0] == self.tile_type
        parts[0] = self.alias_tile_type

        for block_type in self.alias:
            if len(parts) > 1 and parts[1] in self.alias[block_type].sites:
                parts[1] = self.alias[block_type].sites[parts[1]]

        return '.'.join(parts)

    def map_feature_from_segbits(self, feature):
        """ Map from the aliases feature name to the output feature name. """
        parts = feature.split('.')

        assert parts[0] == self.alias_tile_type
        parts[0] = self.tile_type

        for block_type in self.alias:
            if len(parts) > 1 and parts[1] in self.sites_rev_map[block_type]:
                parts[1] = self.sites_rev_map[block_type][parts[1]]

        return '.'.join(parts)

    def match_filter(self, block_type, query_bit):
        word = query_bit.word_bit // bitstream.WORD_SIZE_BITS
        real_word = word - self.alias[block_type].start_offset
        if real_word < 0 or real_word >= self.bits_map[block_type].words:
            return False

        return True

    def match_bitdata(self, block_type, bits, bitdata):
        alias_bits = self.alias_bits_map[block_type]

        for bits_found, alias_feature in self.tile_segbits.match_bitdata(
                block_type, alias_bits, bitdata,
                match_filter=self.match_filter):
            feature = self.map_feature_from_segbits(alias_feature)

            yield (bits_found, feature)

    def feature_to_bits(self, bits_map, feature, address=0):
        if feature in self.ppips:
            return

        alias_feature = self.map_feature_to_segbits(feature)
        for block_type, bit in self.tile_segbits.feature_to_bits(
                self.alias_bits_map, alias_feature, address):
            yield block_type, bit
