#!/usr/bin/env python3

from utils import xjson


def load_tiles(tiles_fn):
    '''
    "$type $tile $grid_x $grid_y $typed_sites"
    typed_sites: foreach t $site_types s $sites
    '''
    tiles = list()

    with open(tiles_fn) as f:
        for line in f:
            # CLBLM_L CLBLM_L_X10Y98 30 106 SLICEL SLICE_X13Y98 SLICEM SLICE_X12Y98
            record = line.split()
            tile_type, tile_name, grid_x, grid_y = record[0:4]
            grid_x, grid_y = int(grid_x), int(grid_y)
            sites = {}
            for i in range(4, len(record), 2):
                site_type, site_name = record[i:i + 2]
                sites[site_name] = site_type
            tile = {
                'type': tile_type,
                'name': tile_name,
                'grid_x': grid_x,
                'grid_y': grid_y,
                'sites': sites,
            }
            tiles.append(tile)

    return tiles


def make_database(tiles):
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
        }

    return database


def run(tiles_fn, json_fn, verbose=False):
    # Load input files
    tiles = load_tiles(tiles_fn)

    # Index input
    database = make_database(tiles)

    # Save
    xjson.pprint(open(json_fn, 'w'), database)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate tilegrid.json from bitstream deltas')

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--out', default='/dev/stdout', help='Output JSON')
    parser.add_argument(
        '--tiles', default='tiles.txt', help='Input tiles.txt tcl output')
    args = parser.parse_args()

    run(args.tiles, args.out, verbose=args.verbose)


if __name__ == '__main__':
    main()
