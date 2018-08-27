#!/usr/bin/env python3

'''
Triaging tool to help understand where we need more timing coverage
Finds correlated variables to help make better test cases
'''

from timfuz import Benchmark, Ar_di2np, loadc_Ads_b, index_names, A_ds2np, simplify_rows
import numpy as np
import glob
import math
import json
import sympy
from collections import OrderedDict
from fractions import Fraction
import random

def fracr(r):
    DELTA = 0.0001

    for i, x in enumerate(r):
        if type(x) is float:
            xi = int(x)
            assert abs(xi - x) < DELTA
            r[i] = xi
    return [Fraction(x) for x in r]

def fracm(m):
    return [fracr(r) for r in m]

def create_matrix(rows, cols):
    ret = np.zeros((rows, cols))
    for rowi in range(rows):
        for coli in range(cols):
            ret[rowi][coli] = random.randint(1, 10)
    return ret

def create_matrix_sparse(rows, cols):
    ret = np.zeros((rows, cols))
    for rowi in range(rows):
        for coli in range(cols):
            if random.randint(0, 5) < 1:
                ret[rowi][coli] = random.randint(1, 10)
    return ret

def run(rows=35, cols=200, verbose=False, encoding='np', sparse=False):
    random.seed(0)
    if sparse:
        mnp = create_matrix_sparse(rows, cols)
    else:
        mnp = create_matrix(rows, cols)
    #print(mnp[0])

    if encoding == 'fraction':
        mfrac = fracm(mnp)
        msym = sympy.Matrix(mfrac)
    elif encoding == 'np':
        msym = sympy.Matrix(mnp)
    else:
        assert 0, 'bad encoding: %s' % encoding

    if verbose:
        print('names')
        print(names)
        print('Matrix')
        sympy.pprint(msym)

    print('%s matrix, %u rows x %u cols, sparse: %s' % (encoding, len(mnp), len(mnp[0]), sparse))
    bench = Benchmark()
    try:
        rref, pivots = msym.rref()
    finally:
        print('rref exiting after %s' % bench)

    if verbose:
        print('Pivots')
        sympy.pprint(pivots)
        print('rref')
        sympy.pprint(rref)

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Timing fuzzer'
    )

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--sparse', action='store_true', help='')
    parser.add_argument('--rows', type=int, help='')
    parser.add_argument('--cols', type=int, help='')
    parser.add_argument('--encoding', default='np', help='')
    args = parser.parse_args()

    run(encoding=args.encoding, rows=args.rows, cols=args.cols, sparse=args.sparse, verbose=args.verbose)

if __name__ == '__main__':
    main()
