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
from prjxray import segment_map
from prjxray.grid_types import BlockType, GridLoc, GridInfo, BitAlias, Bits, BitsInfo, ClockRegion
from prjxray.tile_segbits_alias import TileSegbitsAlias
import re

CLOCK_REGION_RE = re.compile('X([0-9])Y([0-9])')


class Grid(object):
    """ Object that represents grid for a given database.

  Provides methods to inspect grid by name or location.  Also provides mapping
  of segment offsets for particular grid locations and their tile types.
  """

    def __init__(self, db, tilegrid):
        self.db = db
        self.tilegrid = tilegrid
        self.loc = {}
        self.tileinfo = {}

        clock_regions = {}

        for tile in self.tilegrid:
            tileinfo = self.tilegrid[tile]
            grid_loc = GridLoc(tileinfo['grid_x'], tileinfo['grid_y'])
            assert grid_loc not in self.loc
            self.loc[grid_loc] = tile

            bits = {}

            if 'bits' in tileinfo:
                for k in tileinfo['bits']:
                    segment_type = BlockType(k)
                    base_address = int(tileinfo['bits'][k]['baseaddr'], 0)

                    alias = None
                    if 'alias' in tileinfo['bits'][k]:
                        alias = BitAlias(
                            tile_type=tileinfo['bits'][k]['alias']['type'],
                            start_offset=tileinfo['bits'][k]['alias']
                            ['start_offset'],
                            sites=tileinfo['bits'][k]['alias']['sites'],
                        )

                    bits[segment_type] = Bits(
                        base_address=base_address,
                        frames=tileinfo['bits'][k]['frames'],
                        offset=tileinfo['bits'][k]['offset'],
                        words=tileinfo['bits'][k]['words'],
                        alias=alias,
                    )

            clock_region = None
            if 'clock_region' in tileinfo:
                if tileinfo['clock_region'] is not None:
                    if tileinfo['clock_region'] not in clock_regions:
                        m = CLOCK_REGION_RE.fullmatch(tileinfo['clock_region'])
                        assert m is not None, tileinfo['clock_region']

                        clock_regions[tileinfo['clock_region']] = ClockRegion(
                            name=tileinfo['clock_region'],
                            x=int(m.group(1)),
                            y=int(m.group(2)))

                    clock_region = clock_regions[tileinfo['clock_region']]

            self.tileinfo[tile] = GridInfo(
                bits=bits,
                sites=tileinfo['sites'],
                prohibited_sites=tileinfo['prohibited_sites'],
                tile_type=tileinfo['type'],
                pin_functions=tileinfo.get('pin_functions', {}),
                clock_region=clock_region,
            )

        x, y = zip(*self.loc.keys())
        self._dims = (min(x), max(x), min(y), max(y))

    def tiles(self):
        """ Return list of tiles. """
        return self.tileinfo.keys()

    def tile_locations(self):
        """ Return list of tile locations. """
        return self.loc.keys()

    def dims(self):
        """ Returns (x_min, x_max, y_min, y_max) for given Grid. """
        return self._dims

    def is_populated(self, grid_loc):
        return grid_loc in self.loc

    def loc_of_tilename(self, tilename):
        tileinfo = self.tilegrid[tilename]
        return GridLoc(tileinfo['grid_x'], tileinfo['grid_y'])

    def tilename_at_loc(self, grid_loc):
        return self.loc[grid_loc]

    def gridinfo_at_loc(self, grid_loc):
        return self.tileinfo[self.loc[grid_loc]]

    def gridinfo_at_tilename(self, tilename):
        return self.tileinfo[tilename]

    def iter_all_frames(self):
        for tile, tileinfo in self.tileinfo.items():
            for block_type, bits in tileinfo.bits.items():
                yield BitsInfo(
                    block_type=block_type,
                    tile=tile,
                    bits=bits,
                )

    def get_segment_map(self):
        return segment_map.SegmentMap(self)

    def tile_key(self, tilename):
        gridinfo = self.gridinfo_at_tilename(tilename)
        loc = self.loc_of_tilename(tilename)
        tile_type = gridinfo.tile_type

        return (tile_type, loc.grid_x, -loc.grid_y)

    def get_tile_segbits_at_tilename(self, tilename):
        gridinfo = self.gridinfo_at_tilename(tilename)

        # Check to see if alias is present
        any_alias = False
        for block_type, bits in gridinfo.bits.items():
            if bits.alias is not None:
                any_alias = True

        if any_alias:
            return TileSegbitsAlias(self.db, gridinfo.tile_type, gridinfo.bits)
        else:
            return self.db.get_tile_segbits(gridinfo.tile_type)
