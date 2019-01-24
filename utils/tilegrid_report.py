#!/usr/bin/env python3
import simplejson as json
import argparse

def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('tilegrid_json')

    args = parser.parse_args()

    with open(args.tilegrid_json, 'r') as f:
        tilegrid = json.load(f)

    tile_types = {}

    for tile in tilegrid:
        tile_type = tilegrid[tile]['type']
        if tile_type not in tile_types:
            tile_types[tilegrid[tile]['type']] = []

        tile_types[tile_type].append((tile, tilegrid[tile]))

    total_tile_count = 0
    total_have_bits = 0
    for tile_type, tiles in sorted(tile_types.items()):
        if 'NULL' in tile_type:
            continue

        have_bits = 0
        for tile_name, tile in tiles:
            total_tile_count += 1
            if 'bits' in tile and 'CLB_IO_CLK' in tile['bits']:
                have_bits += 1
                total_have_bits += 1

        print('{}: {}/{} ({:.2f} %)'.format(tile_type, have_bits, len(tiles), 100.*float(have_bits)/len(tiles)))

    print('')
    print('Summary: {}/{} ({:.2f} %)'.format(total_have_bits, total_tile_count, 100.*float(total_have_bits)/total_tile_count))

if __name__ == "__main__":
    main()
