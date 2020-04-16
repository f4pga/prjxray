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
WireInGrid = namedtuple('WireInGrid', 'tile grid_x grid_y wire')
Connection = namedtuple('Connection', 'wire_a wire_b')


class Connections(object):
    def __init__(self, tilegrid, tileconn, tile_wires):
        self.grid = tilegrid
        self.tile_wires = tile_wires
        self.coord_to_tile = {}
        self.coord_to_tile_type = {}

        for tile, tile_info in self.grid.items():
            self.coord_to_tile[(tile_info['grid_x'],
                                tile_info['grid_y'])] = tile
            self.coord_to_tile_type[(tile_info['grid_x'],
                                     tile_info['grid_y'])] = tile_info['type']

            # Make sure we have tile type info for every tile in the grid.
            assert tile_info['type'] in self.tile_wires, (
                tile_info['type'], self.tile_wires.keys())

        self.potential_connections = {}

        for conn in tileconn:
            grid_deltas = conn['grid_deltas']
            tile_types = conn['tile_types']

            for pairs in conn['wire_pairs']:
                key = (tile_types[0], pairs[0])
                if key not in self.potential_connections:
                    self.potential_connections[key] = []
                self.potential_connections[key].append(
                    (grid_deltas, tile_types[1], pairs[1]))

    def all_possible_connections_from(self, wire_in_grid):
        tile_type = self.coord_to_tile_type[(
            wire_in_grid.grid_x, wire_in_grid.grid_y)]

        key = (tile_type, wire_in_grid.wire)

        if key not in self.potential_connections:
            return

        for relative_coord, target_tile_type, target_wire in (
                self.potential_connections[key]):
            rel_x, rel_y = relative_coord
            target_coord = (
                wire_in_grid.grid_x + rel_x, wire_in_grid.grid_y + rel_y)

            if target_coord in self.coord_to_tile_type:
                if self.coord_to_tile_type[target_coord] == target_tile_type:
                    yield Connection(
                        wire_in_grid,
                        WireInGrid(
                            tile=self.coord_to_tile[target_coord],
                            grid_x=target_coord[0],
                            grid_y=target_coord[1],
                            wire=target_wire))

    def get_connections(self):
        """ Yields Connection objects that represent all connections present in
    the grid based on tileconn """
        for tile, tile_info in self.grid.items():
            for wire in self.tile_wires[tile_info['type']]:
                wire_in_grid = WireInGrid(
                    tile=tile,
                    grid_x=tile_info['grid_x'],
                    grid_y=tile_info['grid_y'],
                    wire=wire)
                for potential_connection in self.all_possible_connections_from(
                        wire_in_grid):
                    yield potential_connection
