#!/usr/bin/env python3

# https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.optimize.linprog.html
from scipy.optimize import linprog
from timfuz import Benchmark, Ar_di2np, Ar_ds2t, A_di2ds, A_ds2di, simplify_rows, loadc_Ads_b, index_names, A_ds2np, load_sub, run_sub_json, A_ub_np2d, print_eqns, print_eqns_np, Ads2bounds, loadc_Ads_raw, instances
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

def gen_group(fnin, sub_json, strict=False, verbose=False):
    print('Loading data')
    # FIXME: preserve corners
    Ads, b = loadc_Ads_b([fnin], corner=None, ico=True)

    print('Sub: %u rows' % len(Ads))
    iold = instances(Ads)
    names_old = index_names(Ads)
    run_sub_json(Ads, sub_json, strict=strict, verbose=verbose)
    names = index_names(Ads)
    print("Sub: %u => %u names" % (len(names_old), len(names)))
    print('Sub: %u => %u instances' % (iold, instances(Ads)))

    for row_ds, row_b in zip(Ads, b):
        yield row_ds, [row_b for _ in range(4)]

def run(fnin, fnout, sub_json, corner=None, strict=False, verbose=False):
    with open(fnout, 'w') as fout:
        fout.write('ico,fast_max fast_min slow_max slow_min,rows...\n')
        for row_ds, row_bs in gen_group(fnin, sub_json, strict=strict):
            row_ico = 1
            items = [str(row_ico), ' '.join([str(x) for x in row_bs])]
            for k, v in sorted(row_ds.items()):
                items.append('%u %s' % (v, k))
            fout.write(','.join(items) + '\n')

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Solve timing solution'
    )

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--massage', action='store_true', help='')
    parser.add_argument('--strict', action='store_true', help='')
    parser.add_argument('--sub-csv', help='')
    parser.add_argument('--sub-json', required=True, help='Group substitutions to make fully ranked')
    parser.add_argument('fnin', default=None, help='input timing delay .csv')
    parser.add_argument('fnout', default=None, help='output timing delay .csv')
    args = parser.parse_args()
    # Store options in dict to ease passing through functions
    bench = Benchmark()

    sub_json = load_sub(args.sub_json)

    try:
        run(args.fnin, args.fnout, sub_json=sub_json, strict=args.strict, verbose=args.verbose)
    finally:
        print('Exiting after %s' % bench)

if __name__ == '__main__':
    main()
