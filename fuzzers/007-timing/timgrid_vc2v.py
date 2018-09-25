#!/usr/bin/env python3

import sys
import os
import time
import json
from collections import OrderedDict
import timfuz

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


def merge_bdict(vi, vo):
    '''
    vi: input dictionary
    vo: output dictionary
    values are corner delay 4 tuples
    '''

    for name, bis in vi.items():
        bos = vo.get(name, [None, None, None, None])
        for cornerk, corneri in corner_s2i.items():
            bo = bos[corneri]
            bi = bis[corneri]
            # no new data
            if bi is None:
                pass
            # no previous data
            elif bo is None:
                bos[corneri] = bi
            # combine
            else:
                minmax = corner2minmax[cornerk]
                bos[corneri] = minmax(bi, bo)


def merge_tiles(tileji, tilejo):
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

    for tilek, tilevi in tileji.items():
        # No previous data? Copy
        tilevo = tilejo.get(tilek, None)
        if tilevo is None:
            tilejo[tilek] = tilevi
        # Otherwise combine
        else:
            merge_bdict(tilevi['pips'], tilevo['pips'])
            merge_bdict(tilevi['wires'], tilevo['wires'])


def merge_sites(siteji, sitejo):
    for k, vi in siteji.items():
        vo = sitejo.get(k, None)
        # No previous data? Copy
        if vo is None:
            sitejo[k] = vi
        # Otherwise combine
        else:
            merge_bdict(vi, vo)


def build_tilejo(fnins):
    # merge all inputs into blank output
    tilejo = {"tiles": {}, "sites": {}}
    for fnin in fnins:
        tileji = json.load(open(fnin, 'r'))

        merge_tiles(tileji['tiles'], tilejo['tiles'])
        merge_sites(tileji['sites'], tilejo['sites'])

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

    print('')
    print('minmax: %u / %u pairs bad pairs adjusted' % (bad, checks))
    timfuz.tilej_stats(tilej)


def run(fnins, fnout, verbose=False):
    tilejo = build_tilejo(fnins)
    check_corner_minmax(tilejo)
    # XXX: check fast vs slow?
    # check_corners_minmax(tilejo)
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
    parser.add_argument(
        '--out', required=True, help='Combined timgrid-v.json files')
    parser.add_argument('fnins', nargs='+', help='Input timgrid-vc.json files')
    args = parser.parse_args()

    run(args.fnins, args.out, verbose=False)


if __name__ == '__main__':
    main()
