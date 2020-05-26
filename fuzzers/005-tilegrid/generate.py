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

from utils import xjson


def load_tiles(tiles_fn):
    '''
    "$type $tile $grid_x $grid_y $skip_tile $clock_region $typed_sites"
    typed_sites: foreach t $site_types s $sites
    '''
    tiles = list()

    with open(tiles_fn) as f:
        for line in f:
            # CLBLM_L CLBLM_L_X10Y98 30 106 SLICEL SLICE_X13Y98 SLICEM SLICE_X12Y98
            record = line.split()
            tile_type, tile_name, grid_x, grid_y, skip_tile = record[0:5]
            grid_x, grid_y = int(grid_x), int(grid_y)
            skip_tile = int(skip_tile) != 0
            sites = {}

            # prohibits is the list of sites that the Vivado placer will not
            # place at.
            #
            # Speculation: These sites are prohibited not because the hardware
            # doesn't work, but because the interconnect around these sites is
            # extremely narrow due to the hardblocks to the left and right of
            # tiles.  As a result, these sites should be avoided because
            # congestion and delays when using these sites might be very very
            # high.
            prohibits = []
            clock_region = None
            if len(record) >= 6:
                clock_region = record[5]
                if clock_region == "NA":
                    clock_region = None
                for i in range(6, len(record), 3):
                    site_type, site_name, prohibited = record[i:i + 3]
                    sites[site_name] = site_type
                    if int(prohibited):
                        prohibits.append(site_name)

            if not skip_tile:
                tile = {
                    'type': tile_type,
                    'name': tile_name,
                    'grid_x': grid_x,
                    'grid_y': grid_y,
                    'sites': sites,
                    'prohibited_sites': sorted(prohibits),
                    'clock_region': clock_region,
                }
            else:
                # Replace tiles within the exclude_roi with NULL tiles to
                # ensure no gaps in the tilegrid.
                #
                # The name will reflect the original tile.
                tile = {
                    'type': 'NULL',
                    'name': tile_name,
                    'grid_x': grid_x,
                    'grid_y': grid_y,
                    'sites': {},
                    'prohibited_sites': [],
                    'clock_region': clock_region,
                }

            tiles.append(tile)

    return tiles


def load_pin_functions(pin_func_fn):
    pin_functions = {}

    with open(pin_func_fn) as f:
        for line in f:
            site, pin_func = line.split()
            assert site not in pin_functions, site
            pin_functions[site] = pin_func

    return pin_functions


def make_database(tiles, pin_func):
    # tile database with X, Y, and list of sites
    # tile name as keys
    database = dict()

    for tile in tiles:
        database[tile["name"]] = {
            "type": tile["type"],
            "sites": tile["sites"],
            "grid_x": tile["grid_x"],
            "grid_y": tile["grid_y"],
            "bits": {},
            "pin_functions": {},
            "prohibited_sites": tile['prohibited_sites'],
        }

        if tile["clock_region"]:
            database[tile["name"]]["clock_region"] = tile["clock_region"]

        for site in database[tile["name"]]["sites"]:
            if site in pin_func:
                database[tile["name"]]["pin_functions"][site] = pin_func[site]

    return database


def run(tiles_fn, pin_func_fn, json_fn, verbose=False):
    # Load input files
    tiles = load_tiles(tiles_fn)

    # Read site map
    pin_func = load_pin_functions(pin_func_fn)

    # Index input
    database = make_database(tiles, pin_func)

    # Save
    xjson.pprint(open(json_fn, 'w'), database)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate tilegrid.json from bitstream deltas')

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--out', default='/dev/stdout', help='Output JSON')
    parser.add_argument(
        '--tiles',
        default='tiles.txt',
        help='Input tiles.txt tcl output',
        required=True)
    parser.add_argument(
        '--pin_func', help='List of sites with pin functions', required=True)
    args = parser.parse_args()

    run(args.tiles, args.pin_func, args.out, verbose=args.verbose)


if __name__ == '__main__':
    main()
