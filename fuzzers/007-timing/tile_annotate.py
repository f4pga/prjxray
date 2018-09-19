#!/usr/bin/env python3

import timfuz
from timfuz import loadc_Ads_bs, Ads2bounds

import sys
import os
import time
import json


def run(fns_in, fnout, tile_json_fn, verbose=False):
    # modified in place
    tilej = json.load(open(tile_json_fn, 'r'))

    for fnin in fns_in:
        Ads, bs = loadc_Ads_bs([fnin], ico=True)
        bounds = Ads2bounds(Ads, bs)

        for tile in tilej['tiles'].values():
            pips = tile['pips']
            for k, v in pips.items():
                pips[k] = bounds.get('PIP_' + v, [None, None, None, None])

            wires = tile['wires']
            for k, v in wires.items():
                wires[k] = bounds.get('WIRE_' + v, [None, None, None, None])

    timfuz.tilej_stats(tilej)

    json.dump(
        tilej,
        open(fnout, 'w'),
        sort_keys=True,
        indent=4,
        separators=(',', ': '))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Substitute timgrid timing model names for real timing values')
    parser.add_argument(
        '--timgrid-s',
        default='../../timgrid/build/timgrid-s.json',
        help='tilegrid timing delay symbolic input (timgrid-s.json)')
    parser.add_argument(
        '--out',
        default='build/timgrid-vc.json',
        help='tilegrid timing delay values at corner (timgrid-vc.json)')
    parser.add_argument(
        'fn_ins', nargs='+', help='Input flattened timing csv (flat.csv)')
    args = parser.parse_args()

    run(args.fn_ins, args.out, args.timgrid_s, verbose=False)


if __name__ == '__main__':
    main()
