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
class Roi(object):
    """ Object that represents a Project X-ray ROI.

    Can be used to iterate over tiles and sites within an ROI.

    """

    def __init__(self, db, x1, x2, y1, y2):
        self.grid = db.grid()
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def tile_in_roi(self, grid_loc):
        """ Returns true if grid_loc (GridLoc tuple) is within the ROI. """
        x = grid_loc.grid_x
        y = grid_loc.grid_y
        return self.x1 <= x and x <= self.x2 and self.y1 <= y and y <= self.y2

    def gen_tiles(self, tile_types=None):
        ''' Yield tile names within ROI.

        tile_types: list of tile types to keep, or None for all
        '''

        for tile_name in self.grid.tiles():
            loc = self.grid.loc_of_tilename(tile_name)

            if not self.tile_in_roi(loc):
                continue

            gridinfo = self.grid.gridinfo_at_loc(loc)

            if tile_types is not None and gridinfo.tile_type not in tile_types:
                continue

            yield tile_name

    def gen_sites(self, site_types=None):
        ''' Yield (tile_name, site_name, site_type) within ROI.

        site_types: list of site types to keep, or None for all

        '''

        for tile_name in self.grid.tiles():
            loc = self.grid.loc_of_tilename(tile_name)

            if not self.tile_in_roi(loc):
                continue

            gridinfo = self.grid.gridinfo_at_loc(loc)

            for site_name, site_type in gridinfo.sites.items():
                if site_types is not None and site_type not in site_types:
                    continue

                yield (tile_name, site_name, site_type)
