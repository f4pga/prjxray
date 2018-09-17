#!/usr/bin/env python3

# https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.optimize.linprog.html
from scipy.optimize import linprog
from timfuz import Benchmark, loadc_Ads_bs, load_sub, Ads2bounds, corners2csv, corner_s2i
from timfuz_massage import massage_equations
import numpy as np
import glob
import json
import math
from collections import OrderedDict
from fractions import Fraction
import sys
import datetime
import os
import time


def gen_flat(fnin, sub_json, corner=None):
    Ads, bs = loadc_Ads_bs([fnin], ico=True)
    bounds = Ads2bounds(Ads, bs)
    zeros = set()
    nonzeros = set()

    for bound_name, bound_bs in bounds.items():
        sub = sub_json['subs'].get(bound_name, None)
        if sub:
            # put entire delay into pivot
            pivot = sub_json['pivots'][bound_name]
            assert pivot not in zeros
            nonzeros.add(pivot)
            non_pivot = set(sub.keys() - set([pivot]))
            #for name in non_pivot:
            #    assert name not in nonzeros, (pivot, name, nonzeros)
            zeros.update(non_pivot)
            yield pivot, bound_bs
        else:
            nonzeros.add(bound_name)
            yield bound_name, bound_bs
    # non-pivots can appear multiple times, but they should always be zero
    # however, due to substitution limitations, just warn
    violations = zeros.intersection(nonzeros)
    if len(violations):
        print('WARNING: %s non-0 non-pivot' % (len(violations)))

    # XXX: how to best handle these?
    # should they be fixed 0?
    if corner:
        zero_row = [None, None, None, None]
        zero_row[corner_s2i[corner]] = 0
        for zero in zeros - violations:
            yield zero, zero_row


def run(fns_in, fnout, sub_json, corner=None, sort=False, verbose=False):
    '''
    if sort:
        sortf = sorted
    else:
        sortf = lambda x: x
    '''

    with open(fnout, 'w') as fout:
        fout.write('ico,fast_max fast_min slow_max slow_min,rows...\n')
        for fnin in fns_in:
            #for name, corners in sortf(gen_flat(fnin, sub_json)):
            for name, corners in gen_flat(fnin, sub_json, corner=corner):
                row_ico = 1
                items = [str(row_ico), corners2csv(corners)]
                items.append('%u %s' % (1, name))
                fout.write(','.join(items) + '\n')


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Substitute .csv to ungroup correlated symbols')

    parser.add_argument('--verbose', action='store_true', help='')
    #parser.add_argument('--sort', action='store_true', help='')
    parser.add_argument('--sub-csv', help='')
    parser.add_argument(
        '--sub-json',
        required=True,
        help='Group substitutions to make fully ranked')
    parser.add_argument('--corner', default=None, help='')
    parser.add_argument('--out', default=None, help='output timing delay .csv')
    parser.add_argument(
        'fns_in',
        default=None,
        help='input timing delay .csv (NOTE: must be single column)')
    args = parser.parse_args()
    # Store options in dict to ease passing through functions
    bench = Benchmark()

    sub_json = load_sub(args.sub_json)

    try:
        run(
            args.fns_in,
            args.out,
            sub_json=sub_json,
            #sort=args.sort,
            verbose=args.verbose,
            corner=args.corner)
    finally:
        print('Exiting after %s' % bench)


if __name__ == '__main__':
    main()
