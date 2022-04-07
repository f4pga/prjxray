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
import os.path
import csv
import pickle
import re
from collections import namedtuple

from prjxray.util import OpenSafeFile


def read_root_csv(root_dir):
    """ Reads root.csv from raw db directory.

  This should only be used during database generation.

  """
    tiles = {}
    nodes = []

    with OpenSafeFile(os.path.join(root_dir, 'root.csv')) as f:
        for d in csv.DictReader(f):
            if d['filetype'] == 'tile':
                if d['subtype'] not in tiles:
                    tiles[d['subtype']] = []

                tiles[d['subtype']].append(
                    os.path.join(root_dir, d['filename']))
            elif d['filetype'] == 'node':
                nodes.append(os.path.join(root_dir, d['filename']))

    return tiles, nodes


def verify_nodes(raw_nodes, nodes, error_nodes):
    """ Compares raw_nodes with generated_nodes and adds errors to error_nodes.

  Args:
    raw_nodes - Iterable of (node name, iterable of wires in node).
    nodes - Iterable of iterable of wires in nodes.
    error_nodes - List to be appended to when an error occurs.  Elements will
                  be 3 tuple of raw node name, raw node, and generated node
                  that did not match.

  """
    wire_nodes = {}
    for node in nodes:
        node_set = set(node)
        for wire in node:
            wire_nodes[wire] = node_set

    for node, raw_node_wires in raw_nodes:
        raw_node_set = set(raw_node_wires)

        for wire in sorted(raw_node_set):
            if wire not in wire_nodes:
                if set((wire, )) != raw_node_set:
                    error_nodes.append((node, tuple(raw_node_set), (wire, )))
            elif wire_nodes[wire] != raw_node_set:
                error_nodes.append(
                    (node, tuple(raw_node_set), tuple(wire_nodes[wire])))


def check_errors(flat_error_nodes, ignored_wires):
    """ Check if error_nodes has errors that are not covered in ignored_wires.

  Args:
    flat_error_nodes - List of error_nodes generated from verify_nodes.
    ignored_wires - List of wires that should be ignored if they were generated.

  """

    error_nodes = {}
    for node, raw_node, generated_nodes in flat_error_nodes:
        if node not in error_nodes:
            error_nodes[node] = {
                'raw_node': set(raw_node),
                'generated_nodes': set(),
            }

        # Make sure all raw nodes are the same.
        assert error_nodes[node]['raw_node'] == set(raw_node)

        error_nodes[node]['generated_nodes'].add(
            tuple(sorted(generated_nodes)))

    for node, error in error_nodes.items():
        combined_generated_nodes = set()
        for generated_node in error['generated_nodes']:
            combined_generated_nodes |= set(generated_node)

        # Make sure there are not extra wires in nodes.
        assert error['raw_node'] == combined_generated_nodes, (node, error)

        good_node = max(error['generated_nodes'], key=lambda x: len(x))
        bad_nodes = error['generated_nodes'] - set((good_node, ))

        # Max sure only single wires are stranded
        assert max(len(generated_node) for generated_node in bad_nodes) == 1

        for generate_node in bad_nodes:
            for wire in generate_node:
                if wire not in ignored_wires:
                    return False

    return True


class NodeLookup(object):
    def __init__(self):
        self.nodes = {}

    def load_from_nodes(self, nodes):
        self.nodes = nodes

    def load_from_root_csv(self, nodes):
        import pyjson5 as json5
        import progressbar
        for node in progressbar.progressbar(nodes):
            with OpenSafeFile(node) as f:
                node_wires = json5.load(f)
                assert node_wires['node'] not in self.nodes
                self.nodes[node_wires['node']] = node_wires['wires']

    def load_from_file(self, fname):
        with OpenSafeFile(fname, 'rb') as f:
            self.nodes = pickle.load(f)

    def save_to_file(self, fname):
        with OpenSafeFile(fname, 'wb') as f:
            pickle.dump(self.nodes, f)

    def site_pin_node_to_wires(self, tile, node):
        if node is None:
            return

        node_wires = self.nodes[node]

        for wire in node_wires:
            if wire['wire'].startswith(tile + '/'):
                yield wire['wire'][len(tile) + 1:]

    def wires_for_tile(self, tile):
        for node in self.nodes.values():
            for wire in node:
                if wire['wire'].startswith(tile + '/'):
                    yield wire['wire'][len(tile) + 1:]


def compare_prototype_site(proto_a, proto_b):
    """ Compare two proto site type.

  Will assert if prototypes are not equivalent.

  """
    assert proto_a == proto_b, repr((proto_a, proto_b))


# All site names appear to follow the pattern <type>_X<abs coord>Y<abs coord>.
# Generally speaking, only the tile relatively coordinates are required to
# assemble arch defs, so we re-origin the coordinates to be relative to the tile
# (e.g. start at X0Y0) and discard the prefix from the name.
SITE_COORDINATE_PATTERN = re.compile('^(.+)_X([0-9]+)Y([0-9]+)$')

SiteCoordinate = namedtuple('SiteCoordinate', 'prefix x_coord y_coord')


def get_site_coordinate_from_name(name):
    """
    >>> get_site_coordinate_from_name('SLICE_X1Y0')
    SiteCoordinate(prefix='SLICE', x_coord=1, y_coord=0)

    >>> get_site_coordinate_from_name('SLICE_X0Y0')
    SiteCoordinate(prefix='SLICE', x_coord=0, y_coord=0)

    >>> get_site_coordinate_from_name('INT_L_X500Y999')
    SiteCoordinate(prefix='INT_L', x_coord=500, y_coord=999)

    """
    coordinate = SITE_COORDINATE_PATTERN.match(name)
    assert coordinate is not None, name

    return SiteCoordinate(
        prefix=coordinate.group(1),
        x_coord=int(coordinate.group(2)),
        y_coord=int(coordinate.group(3)),
    )


def get_site_prefix_from_name(name):
    """
    Returns the prefix of a site from its name
    """
    coordinate = SITE_COORDINATE_PATTERN.match(name)
    assert coordinate is not None, name

    return coordinate.group(1)


def find_origin_coordinate(site_name, site_names):
    """
    Find the coordinates of each site within the tile, and then subtract the
    smallest coordinate to re-origin them all to be relative to the tile.
    """

    x_coords = []
    y_coords = []
    for site in site_names:
        coordinate = get_site_coordinate_from_name(site)
        site_name_prefix = get_site_prefix_from_name(site_name)
        if coordinate.prefix == site_name_prefix:
            x_coords.append(coordinate.x_coord)
            y_coords.append(coordinate.y_coord)

    if len(x_coords) == 0 or len(y_coords) == 0:
        return 0, 0

    min_x_coord = min(x_coords)
    min_y_coord = min(y_coords)

    return min_x_coord, min_y_coord
