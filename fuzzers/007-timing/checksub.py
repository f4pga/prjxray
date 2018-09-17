#!/usr/bin/env python3

from timfuz import Benchmark, Ar_di2np, Ar_ds2t, A_di2ds, A_ds2di, loadc_Ads_b, index_names, A_ds2np, load_sub, run_sub_json
import numpy as np
import glob
import json
import math
from collections import OrderedDict
from fractions import Fraction


def Adi2matrix_random(A_ubd, b_ub, names):
    # random assignment
    # was making some empty rows

    A_ret = [np.zeros(len(names)) for _i in range(len(names))]
    b_ret = np.zeros(len(names))

    for row, b in zip(A_ubd, b_ub):
        # Randomly assign to a row
        dst_rowi = random.randint(0, len(names) - 1)
        rownp = Ar_di2np(row, cols=len(names), sf=1)

        A_ret[dst_rowi] = np.add(A_ret[dst_rowi], rownp)
        b_ret[dst_rowi] += b
    return A_ret, b_ret


def Ads2matrix_linear(Ads, b):
    names, Adi = A_ds2di(Ads)
    cols = len(names)
    rows_out = len(b)

    A_ret = [np.zeros(cols) for _i in range(rows_out)]
    b_ret = np.zeros(rows_out)

    dst_rowi = 0
    for row_di, row_b in zip(Adi, b):
        row_np = Ar_di2np(row_di, cols)

        A_ret[dst_rowi] = np.add(A_ret[dst_rowi], row_np)
        b_ret[dst_rowi] += row_b
        dst_rowi = (dst_rowi + 1) % rows_out
    return A_ret, b_ret


def pmatrix(Anp, s):
    import sympy
    msym = sympy.Matrix(Anp)
    print(s)
    sympy.pprint(msym)


def pds(Ads, s):
    names, Anp = A_ds2np(Ads)
    pmatrix(Anp, s)
    print('Names: %s' % (names, ))


def run(fns_in, sub_json=None, verbose=False):
    # arbitrary...data is thrown away
    corner = "slow_max"

    Ads, b = loadc_Ads_b(fns_in, corner, ico=True)

    if sub_json:
        print('Subbing JSON %u rows' % len(Ads))
        #pds(Ads, 'Orig')
        names_old = index_names(Ads)
        run_sub_json(Ads, sub_json, verbose=verbose)
        names_new = index_names(Ads)
        print("Sub: %u => %u names" % (len(names_old), len(names_new)))
        print(names_new)
        print('Subbed JSON %u rows' % len(Ads))
        names = names_new
        #pds(Ads, 'Sub')
    else:
        names = index_names(Ads)

    # Squash into a matrix
    # A_ub2, b_ub2 = Adi2matrix_random(A_ubd, b, names)
    Amat, _bmat = Ads2matrix_linear(Ads, b)
    #pmatrix(Amat, 'Matrix')
    '''
    The matrix must be fully ranked to even be considered reasonable
    Even then, floating point error *possibly* could make it fully ranked, although probably not since we have whole numbers
    Hence the slogdet check
    '''
    print
    # https://docs.scipy.org/doc/numpy-dev/reference/generated/numpy.linalg.matrix_rank.html
    rank = np.linalg.matrix_rank(Amat)
    print('rank: %s / %d col' % (rank, len(names)))
    # doesn't work on non-square matrices
    if 0:
        # https://docs.scipy.org/doc/numpy-1.14.0/reference/generated/numpy.linalg.slogdet.html
        sign, logdet = np.linalg.slogdet(Amat)
        # If the determinant is zero, then sign will be 0 and logdet will be -Inf
        if sign == 0 and logdet == float('-inf'):
            print('slogdet :( : 0')
        else:
            print('slogdet :) : %s, %s' % (sign, logdet))
    if rank != len(names):
        raise Exception(
            "Matrix not fully ranked w/ %u / %u" % (rank, len(names)))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Check sub.json solution feasibility')

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--sub-json', help='')
    parser.add_argument('fns_in', nargs='*', help='timing3.csv input files')
    args = parser.parse_args()
    # Store options in dict to ease passing through functions
    bench = Benchmark()

    fns_in = args.fns_in
    if not fns_in:
        fns_in = glob.glob('specimen_*/timing3.csv')

    sub_json = None
    if args.sub_json:
        sub_json = load_sub(args.sub_json)

    try:
        run(sub_json=sub_json, fns_in=fns_in, verbose=args.verbose)
    finally:
        print('Exiting after %s' % bench)


if __name__ == '__main__':
    main()
