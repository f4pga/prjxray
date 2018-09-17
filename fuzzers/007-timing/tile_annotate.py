#!/usr/bin/env python3

import timfuz
from timfuz import loadc_Ads_bs, Ads2bounds

import sys
import os
import time
import json


# corner wokraround
def quad(x):
    return [x for _ in range(4)]


def run(fnin, fnout, tile_json_fn, verbose=False):
    # modified in place
    tilej = json.load(open(tile_json_fn, 'r'))

    # FIXME: all corners
    Ads, bs = loadc_Ads_bs([fnin], ico=True)
    bounds = Ads2bounds(Ads, bs)

    pipn_net = 0
    pipn_solved = [0, 0, 0, 0]
    pipn_covered = [0, 0, 0, 0]
    wiren_net = 0
    wiren_solved = [0, 0, 0, 0]
    wiren_covered = [0, 0, 0, 0]

    for tile in tilej['tiles'].values():
        pips = tile['pips']
        for k, v in pips.items():
            pips[k] = bounds.get('PIP_' + v, [None, None, None, None])
            pipn_net += 1
            for i in range(4):
                if pips[k][i]:
                    pipn_solved[i] += 1
                if pips[k][i] is not None:
                    pipn_covered[i] += 1

        wires = tile['wires']
        for k, v in wires.items():
            wires[k] = bounds.get('WIRE_' + v, [None, None, None, None])
            wiren_net += 1
            for i in range(4):
                if wires[k][i]:
                    wiren_solved[i] += 1
                if wires[k][i] is not None:
                    wiren_covered[i] += 1

    for corner, corneri in timfuz.corner_s2i.items():
        print('Corner %s' % corner)
        print(
            '  Pips: %u / %u solved, %u / %u covered' %
            (pipn_solved[corneri], pipn_net, pipn_covered[corneri], pipn_net))
        print(
            '  Wires: %u / %u solved, %u / %u covered' % (
                wiren_solved[corneri], wiren_net, wiren_covered[corneri],
                wiren_net))

    json.dump(
        tilej,
        open(fnout, 'w'),
        sort_keys=True,
        indent=4,
        separators=(',', ': '))


def main():
    import argparse

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--tile-json', default='tiles.json', help='')
    parser.add_argument('fnin', default=None, help='Flattened timing csv')
    parser.add_argument('fnout', default=None, help='output tile .json')
    args = parser.parse_args()

    run(args.fnin, args.fnout, args.tile_json, verbose=False)


if __name__ == '__main__':
    main()
