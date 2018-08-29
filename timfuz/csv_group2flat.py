#!/usr/bin/env python3

# https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.optimize.linprog.html
from scipy.optimize import linprog
from timfuz import Benchmark, Ar_di2np, Ar_ds2t, A_di2ds, A_ds2di, simplify_rows, loadc_Ads_b, index_names, A_ds2np, load_sub, run_sub_json, A_ub_np2d, print_eqns, print_eqns_np, Ads2bounds, loadc_Ads_raw
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

def gen_flat(fnin, sub_json):
    # FIXME: preserve all bounds
    # Ads, bs = loadc_Ads_raw([csv_fn_in])
    Ads, b = loadc_Ads_b([fnin], corner=None, ico=True)
    bounds = Ads2bounds(Ads, b)
    zeros = set()
    nonzeros = set()

    for bound_name, bound_b in bounds.items():
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
            yield pivot, bound_b
        else:
            nonzeros.add(bound_name)
            yield bound_name, bound_b
    # non-pivots can appear multiple times, but they should always be zero
    # however, due to substitution limitations, just warn
    violations = zeros.intersection(nonzeros)
    if len(violations):
        print('WARNING: %s non-0 non-pivot' % (len(violations)))

    for zero in zeros - violations:
        yield zero, 0

def run(fnin, fnout, sub_json, corner=None, sort=False, verbose=False):
    if sort:
        sortf = sorted
    else:
        sortf = lambda x: x

    with open(fnout, 'w') as fout:
        fout.write('ico,fast_max fast_min slow_max slow_min,rows...\n')
        for name, delay in sortf(gen_flat(fnin, sub_json)):
            row_ico = 1
            corners = [delay for _ in range(4)]
            items = [str(row_ico), ' '.join([str(x) for x in corners])]
            items.append('%u %s' % (1, name))
            fout.write(','.join(items) + '\n')

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Solve timing solution'
    )

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--massage', action='store_true', help='')
    parser.add_argument('--sort', action='store_true', help='')
    parser.add_argument('--sub-csv', help='')
    parser.add_argument('--sub-json', required=True, help='Group substitutions to make fully ranked')
    parser.add_argument('fnin', default=None, help='input timing delay .csv')
    parser.add_argument('fnout', default=None, help='output timing delay .csv')
    args = parser.parse_args()
    # Store options in dict to ease passing through functions
    bench = Benchmark()

    sub_json = load_sub(args.sub_json)

    try:
        run(args.fnin, args.fnout, sub_json=sub_json, sort=args.sort, verbose=args.verbose)
    finally:
        print('Exiting after %s' % bench)

if __name__ == '__main__':
    main()
