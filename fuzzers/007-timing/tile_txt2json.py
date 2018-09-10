#!/usr/bin/env python3

import sys
import os
import time
import json

SI_NONE = 0xFFFF
def load_speed_json(f):
    j = json.load(f)
    # Index speed indexes to names
    speed_i2s = {}
    for k, v in j['speed_model'].items():
        i = v['speed_index']
        if i != SI_NONE:
            speed_i2s[i] = k
    return j, speed_i2s

def gen_tiles(fnin, speed_i2s):
    for l in open(fnin):
        # lappend items pip $name $speed_index
        # puts $fp "$type $tile $grid_x $grid_y $items"
        parts = l.strip().split()
        tile_type, tile_name, grid_x, grid_y = parts[0:4]
        grid_x, grid_y = int(grid_x), int(grid_y)
        tuples = parts[4:]
        assert len(tuples) % 3 == 0
        pips = {}
        wires = {}
        for i in range(0, len(tuples), 3):
            ttype, name, speed_index = tuples[i:i+3]
            name_local = name.split('/')[1]
            {
                'pip': pips,
                'wire': wires,
            }[ttype][name_local] = speed_i2s[int(speed_index)]
        yield (tile_type, tile_name, grid_x, grid_y, pips, wires)

def run(fnin, fnout, speed_json_fn, verbose=False):
    speedj, speed_i2s = load_speed_json(open(speed_json_fn, 'r'))

    tiles = {}
    for tile in gen_tiles(fnin, speed_i2s):
        (tile_type, tile_name, grid_x, grid_y, pips, wires) = tile
        this_dat = {'pips': pips, 'wires': wires}
        if tile_type not in tiles:
            tiles[tile_type] = this_dat
        else:
                if tiles[tile_type] != this_dat:
                    print(tile_name, tile_type)
                    print(this_dat)
                    print(tiles[tile_type])
                    assert 0
    
    j = {'tiles': tiles}
    json.dump(j, open(fnout, 'w'), sort_keys=True, indent=4, separators=(',', ': '))

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Solve timing solution'
    )
    parser.add_argument('--speed-json', default='build_speed/speed.json',
        help='Provides speed index to name translation')
    parser.add_argument('fnin', default=None, help='input tcl output .txt')
    parser.add_argument('fnout', default=None, help='output .json')
    args = parser.parse_args()

    run(args.fnin, args.fnout, speed_json_fn=args.speed_json, verbose=False)

if __name__ == '__main__':
    main()
