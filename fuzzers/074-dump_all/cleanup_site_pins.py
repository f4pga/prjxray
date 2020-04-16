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
""" Tool to cleanup site pins JSON dumps.

This tool has two behaviors.  This first is to rename site names from global
coordinates to site local coordinates.  The second is remove the tile prefix
from node names.

For example CLBLM_L_X8Y149 contains two sites named SLICE_X10Y149 and
SLICE_X11Y149. SLICE_X10Y149 becomes X0Y0 and SLICE_X11Y149 becomes X1Y0.
"""

from __future__ import print_function
import json
import json5
import re
import sys
import copy

# All site names appear to follow the pattern <type>_X<abs coord>Y<abs coord>.
# Generally speaking, only the tile relatively coordinates are required to
# assemble arch defs, so we re-origin the coordinates to be relative to the tile
# (e.g. start at X0Y0) and discard the prefix from the name.
SITE_COORDINATE_PATTERN = re.compile('^(.+)_X([0-9]+)Y([0-9]+)$')


def find_origin_coordinate(sites):
    """ Find the coordinates of each site within the tile, and then subtract the
      smallest coordinate to re-origin them all to be relative to the tile.
  """

    if len(sites) == 0:
        return 0, 0

    def inner_():
        for site in sites:
            coordinate = SITE_COORDINATE_PATTERN.match(site['name'])
            assert coordinate is not None, site

            x_coord = int(coordinate.group(2))
            y_coord = int(coordinate.group(3))
            yield x_coord, y_coord

    x_coords, y_coords = zip(*inner_())
    min_x_coord = min(x_coords)
    min_y_coord = min(y_coords)

    return min_x_coord, min_y_coord


def create_site_pin_to_wire_maps(tile_name, nodes):
    """ Create a map from site_pin names to nodes.

  Create a mapping from site pins to tile local wires.  For each node that is
  attached to a site pin, there should only be 1 tile local wire.

  """

    # Remove tile prefix (e.g. CLBLM_L_X8Y149/) from node names.
    # Routing resources will not have the prefix.
    tile_prefix = tile_name + '/'
    site_pin_to_wires = {}

    for node in nodes:
        if len(node['site_pins']) == 0:
            continue

        wire_names = [
            wire for wire in node['wires'] if wire.startswith(tile_prefix)
        ]
        assert len(wire_names) == 1, (node, tile_prefix)

        for site_pin in node["site_pins"]:
            assert site_pin not in site_pin_to_wires
            site_pin_to_wires[site_pin] = wire_names[0]

    return site_pin_to_wires


def main():
    site_pins = json5.load(sys.stdin)

    output_site_pins = {}
    output_site_pins["tile_type"] = site_pins["tile_type"]
    output_site_pins["sites"] = copy.deepcopy(site_pins["sites"])

    site_pin_to_wires = create_site_pin_to_wire_maps(
        site_pins['tile_name'], site_pins['nodes'])
    min_x_coord, min_y_coord = find_origin_coordinate(site_pins['sites'])

    for site in output_site_pins['sites']:
        orig_site_name = site['name']
        coordinate = SITE_COORDINATE_PATTERN.match(orig_site_name)

        x_coord = int(coordinate.group(2))
        y_coord = int(coordinate.group(3))
        site['name'] = 'X{}Y{}'.format(
            x_coord - min_x_coord, y_coord - min_y_coord)
        site['prefix'] = coordinate.group(1)
        site['x_coord'] = x_coord - min_x_coord
        site['y_coord'] = y_coord - min_y_coord

        for site_pin in site['site_pins']:
            assert site_pin['name'].startswith(orig_site_name + '/')
            if site_pin['name'] in site_pin_to_wires:
                site_pin['wire'] = site_pin_to_wires[site_pin['name']]
            else:
                print(
                    (
                        '***WARNING***: Site pin {} for tile type {} is not connected, '
                        'make sure all instaces of this tile type has this site_pin '
                        'disconnected.').format(
                            site_pin['name'], site_pins['tile_type']),
                    file=sys.stderr)

            site_pin['name'] = site_pin['name'][len(orig_site_name) + 1:]

    json.dumps(output_site_pins, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
