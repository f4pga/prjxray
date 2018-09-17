#!/usr/bin/env python3

import sys
import os
import time
import json
from collections import OrderedDict

corner_s2i = OrderedDict(
    [
        ('fast_max', 0),
        ('fast_min', 1),
        ('slow_max', 2),
        ('slow_min', 3),
    ])

corner2minmax = {
    'fast_max': max,
    'fast_min': min,
    'slow_max': max,
    'slow_min': min,
}


def build_tilejo(fnins):
    '''
    {
        "tiles": {
            "BRKH_B_TERM_INT": {
                "pips": {},
                "wires": {
                    "B_TERM_UTURN_INT_ER1BEG0": [
                        null,
                        null,
                        93,
                        null
                    ],
    '''

    tilejo = {"tiles": {}}
    for fnin in fnins:
        tileji = json.load(open(fnin, 'r'))
        for tilek, tilevi in tileji['tiles'].items():
            # No previous data? Copy
            tilevo = tilejo['tiles'].get(tilek, None)
            if tilevo is None:
                tilejo['tiles'][tilek] = tilevi
            # Otherwise combine
            else:

                def process_type(etype):
                    for pipk, pipvi in tilevi[etype].items():
                        pipvo = tilevo[etype][pipk]
                        for cornerk, corneri in corner_s2i.items():
                            cornervo = pipvo[corneri]
                            cornervi = pipvi[corneri]
                            # no new data
                            if cornervi is None:
                                pass
                            # no previous data
                            elif cornervo is None:
                                pipvo[corneri] = cornervi
                            # combine
                            else:
                                minmax = corner2minmax[cornerk]
                                pipvo[corneri] = minmax(cornervi, cornervo)

                process_type('pips')
                process_type('wires')
    return tilejo


def check_corner_minmax(tilej, verbose=False):
    # Post processing pass looking for min/max inconsistencies
    # Especially an issue due to complexities around under-constrained elements
    # (ex: pivots set to 0 delay)
    print('Checking for min/max consistency')
    checks = 0
    bad = 0
    for tilev in tilej['tiles'].values():

        def process_type(etype):
            nonlocal checks
            nonlocal bad

            for pipk, pipv in tilev[etype].items():
                for corner in ('slow', 'fast'):
                    mini = corner_s2i[corner + '_min']
                    minv = pipv[mini]
                    maxi = corner_s2i[corner + '_max']
                    maxv = pipv[maxi]
                    if minv is not None and maxv is not None:
                        checks += 1
                        if minv > maxv:
                            if verbose:
                                print(
                                    'WARNING: element %s %s min/max adjusted on corner %s'
                                    % (etype, pipk, corner))
                            bad += 1
                            pipv[mini] = maxv
                            pipv[maxi] = minv

        process_type('pips')
        process_type('wires')
    print('minmax: %u / %u bad' % (bad, checks))


def check_corners_minmax(tilej, verbose=False):
    # TODO: check fast vs slow
    pass


def run(fnins, fnout, verbose=False):
    tilejo = build_tilejo(fnins)
    check_corner_minmax(tilejo)
    check_corners_minmax(tilejo)
    json.dump(
        tilejo,
        open(fnout, 'w'),
        sort_keys=True,
        indent=4,
        separators=(',', ': '))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Combine multiple tile corners into one .json file')
    parser.add_argument('--out', required=True, help='Combined .json file')
    parser.add_argument('fnins', nargs='+', help='Input .json files')
    args = parser.parse_args()

    run(args.fnins, args.out, verbose=False)


if __name__ == '__main__':
    main()
