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
class Overlay(object):
    """ Object that represents an overlay.

    Can be used to iterate over tiles and sites not inside a partition region.

    """

    def __init__(self, region_dict):
        self.region_dict = region_dict

    def tile_in_roi(self, grid_loc):
        """ Returns true if grid_loc (GridLoc tuple) is within the overlay. """
        x = grid_loc.grid_x
        y = grid_loc.grid_y
        for _, bounds in self.region_dict.items():
            x1, x2, y1, y2 = bounds
            if x1 <= x and x <= x2 and y1 <= y and y <= y2:
                return False
        return True
