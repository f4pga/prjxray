#!/usr/bin/env python3

from timfuz import Benchmark, Ar_di2np, Ar_ds2t, A_di2ds, A_ds2di, simplify_rows, loadc_Ads_b, index_names, A_ds2np
import numpy as np
import glob
import json
import math
from collections import OrderedDict

# check for issues that may be due to round off error
STRICT = 0

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

def row_sub_syms(row, sub_json, verbose=False):
    if 0 and verbose:
        print("")
        print(row.items())

    delsyms = 0
    for k in sub_json['drop_names']:
        try:
            del row[k]
            delsyms += 1
        except KeyError:
            pass
    if verbose:
        print("Deleted %u symbols" % delsyms)

    if verbose:
        print('Checking pivots')
        print(sorted(row.items()))
        for group, pivot in sorted(sub_json['pivots'].items()):
            if pivot not in row:
                continue
            n = row[pivot]
            print('  pivot %u %s' % (n, pivot))

    for group, pivot in sorted(sub_json['pivots'].items()):
        if pivot not in row:
            continue

        # take the sub out n times
        # note constants may be negative
        n = row[pivot]
        if verbose:
            print('pivot %i %s' % (n, pivot))
        for subk, subv in sorted(sub_json['subs'][group].items()):
            oldn = row.get(subk, 0)
            rown = oldn - n * subv
            if verbose:
                print("  %s: %d => %d" % (subk, oldn, rown))
            if rown == 0:
                # only becomes zero if didn't previously exist
                del row[subk]
                if verbose:
                    print("    del")
            else:
                row[subk] = rown
        row[group] = n
        assert pivot not in row

    # after all constants are applied, the row should end up positive?
    # numeric precision issues may limit this
    # Ex: AssertionError: ('PIP_BSW_2ELSING0', -2.220446049250313e-16)
    if STRICT:
        for k, v in sorted(row.items()):
            assert v > 0, (k, v)

def run_sub_json(Ads, sub_json, verbose=False):
    nrows = 0
    nsubs = 0

    ncols_old = 0
    ncols_new = 0

    print('Subbing %u rows' % len(Ads))
    prints = set()

    for rowi, row in enumerate(Ads):
        if 0 and verbose:
            print(row)
        if verbose:
            print('')
            print('Row %u w/ %u elements' % (rowi, len(row)))

        row_orig = dict(row)
        row_sub_syms(row, sub_json, verbose=verbose)
        nrows += 1
        if row_orig != row:
            nsubs += 1
            if verbose:
                rowt = Ar_ds2t(row)
                if rowt not in prints:
                    print('row', row)
                    prints.add(rowt)
        ncols_old += len(row_orig)
        ncols_new += len(row)

    if verbose:
        print('')

    print("Sub: %u / %u rows changed" % (nsubs, nrows))
    print("Sub: %u => %u cols" % (ncols_old, ncols_new))

def pmatrix(Anp, s):
    import sympy
    msym = sympy.Matrix(Anp)
    print(s)
    sympy.pprint(msym)

def pds(Ads, s):
    names, Anp = A_ds2np(Ads)
    pmatrix(Anp, s)
    print('Names: %s' % (names,))

def run(fns_in, sub_json=None, verbose=False, corner=None):
    Ads, b = loadc_Ads_b(fns_in, corner, ico=True)

    # Remove duplicate rows
    # is this necessary?
    # maybe better to just add them into the matrix directly
    #Ads, b = simplify_rows(Ads, b)

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
    print('rank: %s / %d col' % (np.linalg.matrix_rank(Amat), len(names)))
    if 0:
        # https://docs.scipy.org/doc/numpy-1.14.0/reference/generated/numpy.linalg.slogdet.html
        sign, logdet = np.linalg.slogdet(Amat)
        # If the determinant is zero, then sign will be 0 and logdet will be -Inf
        if sign == 0 and logdet == float('-inf'):
            print('slogdet :( : 0')
        else:
            print('slogdet :) : %s, %s' % (sign, logdet))

def load_sub(fn):
    delta = 0.001
    j = json.load(open(fn, 'r'))

    # convert groups to use integer constants
    # beware of roundoff error
    # if we round poorly here, it won't give incorrect results later, but may make it fail to find a good solution

    if 'pivots' in j:
        print('pivots: using existing')
    else:
        print('pivots: guessing')

        pivots = OrderedDict()
        j['pivots'] = pivots

        for name, vals in sorted(j['subs'].items()):
            pivot = None
            for k, v in vals.items():
                if STRICT:
                    vi = int(round(v))
                    assert abs(vi - v) < delta
                    vals[k] = vi
                else:
                    vals[k] = float(v)

                # there may be more than one acceptable pivot
                # take the first
                if v == 1 and pivot is None:
                    pivot = k
            assert pivot is not None
            pivots[name] = pivot

    return j

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Check sub.json solution feasibility'
    )

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--sub-json', help='')
    parser.add_argument('--corner', default="slow_max", help='')
    parser.add_argument(
        'fns_in',
        nargs='*',
        help='timing3.txt input files')
    args = parser.parse_args()
    # Store options in dict to ease passing through functions
    bench = Benchmark()

    fns_in = args.fns_in
    if not fns_in:
        fns_in = glob.glob('specimen_*/timing3.txt')

    sub_json = None
    if args.sub_json:
        sub_json = load_sub(args.sub_json)

    try:
        run(sub_json=sub_json,
            fns_in=fns_in, verbose=args.verbose, corner=args.corner)
    finally:
        print('Exiting after %s' % bench)

if __name__ == '__main__':
    main()
