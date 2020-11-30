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
class NodeModel():
    """ Node lookup model

    Terminology:
     Wire - A segment of metal in a tile
     Node - A connected set of wires

    This class can provide a list of nodes, the wires in a node and the node
    that a wire belongs too.

    The name of node is always the name of one wire in the node.

    It is recommended that this class be constructed by calling
    Database.node_model rather than constructing this class directly.

    """

    def __init__(
            self, grid, connections, tile_wires, node_wires, progressbar=None):
        self.grid = grid
        self.connections = connections
        self.tile_wires = tile_wires
        self.specific_node_wires = set(node_wires['specific_node_wires'])

        node_pattern_wires = node_wires['node_pattern_wires']
        self.node_pattern_wires = {}
        for tile_type in node_pattern_wires:
            assert tile_type not in self.node_pattern_wires
            self.node_pattern_wires[tile_type] = set(
                node_pattern_wires[tile_type])

        for tile_type in self.tile_wires:
            if tile_type not in self.node_pattern_wires:
                self.node_pattern_wires[tile_type] = set()

        self.nodes = None

        self.wire_to_node_map = None

        if progressbar is None:
            self.progressbar = lambda x: x
        else:
            self.progressbar = progressbar

    def _build_nodes(self):
        tile_wire_map = {}
        wires = {}
        flat_wires = []

        for tile in self.progressbar(self.grid.tiles()):
            gridinfo = self.grid.gridinfo_at_tilename(tile)
            tile_type = gridinfo.tile_type

            for wire in self.tile_wires[tile_type]:
                wire_pkey = len(flat_wires)
                tile_wire_map[(tile, wire)] = wire_pkey
                flat_wires.append((tile, wire))
                wires[wire_pkey] = None

        for connection in self.progressbar(self.connections.get_connections()):
            a_pkey = tile_wire_map[(
                connection.wire_a.tile, connection.wire_a.wire)]
            b_pkey = tile_wire_map[(
                connection.wire_b.tile, connection.wire_b.wire)]

            a_node = wires[a_pkey]
            b_node = wires[b_pkey]

            if a_node is None:
                a_node = set((a_pkey, ))

            if b_node is None:
                b_node = set((b_pkey, ))

            if a_node is not b_node:
                a_node |= b_node

                for wire in a_node:
                    wires[wire] = a_node

        nodes = {}
        for wire_pkey, node in self.progressbar(wires.items()):
            if node is None:
                node = set((wire_pkey, ))

            assert wire_pkey in node

            nodes[id(node)] = node

        def get_node_wire_for_wires(wire_pkeys):
            if len(wire_pkeys) == 1:
                for wire_pkey in wire_pkeys:
                    return flat_wires[wire_pkey]

            for wire_pkey in wire_pkeys:
                tile, wire = flat_wires[wire_pkey]

                if '{}/{}'.format(tile, wire) in self.specific_node_wires:
                    return tile, wire

            for wire_pkey in wire_pkeys:
                tile, wire = flat_wires[wire_pkey]

                gridinfo = self.grid.gridinfo_at_tilename(tile)

                if wire in self.node_pattern_wires[gridinfo.tile_type]:
                    return tile, wire

            return None

        self.nodes = {}
        for node_wire_pkeys in self.progressbar(nodes.values()):
            node_wire = get_node_wire_for_wires(node_wire_pkeys)
            if node_wire is None:
                continue

            self.nodes[node_wire] = [
                flat_wires[wire_pkey] for wire_pkey in node_wire_pkeys
            ]

    def get_nodes(self):
        """ Return a set of node names. """
        if self.nodes is None:
            self._build_nodes()

        return self.nodes.keys()

    def get_wires_for_node(self, tile, wire):
        """ Get wires in node named for specified tile and wire. """
        if self.nodes is None:
            self._build_nodes()

        return self.nodes[tile, wire]

    def _build_wire_to_node_map(self):
        self.wire_to_node_map = {}

        if self.nodes is None:
            self._build_nodes()

        for node, wires in self.nodes.items():
            for tile_wire in wires:
                assert tile_wire not in self.wire_to_node_map
                self.wire_to_node_map[tile_wire] = node

    def get_node_for_wire(self, tile, wire):
        """ Get node for specified tile and wire. """
        if self.wire_to_node_map is None:
            self._build_wire_to_node_map()

        return self.wire_to_node_map[tile, wire]
