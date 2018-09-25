#!/usr/bin/env python3

from timfuz import simplify_rows, loadc_Ads_b, index_names, A_ds2np, run_sub_json, print_eqns, Ads2bounds, instances, SimplifiedToZero, allow_zero_eqns, corner_s2i, acorner2csv
from timfuz_massage import massage_equations
import numpy as np
import sys
import math


def check_feasible(A_ub, b_ub):
    '''
    Put large timing constants into the equations
    See if that would solve it

    Its having trouble giving me solutions as this gets bigger
    Make a terrible baseline guess to confirm we aren't doing something bad
    '''

    sys.stdout.write('Check feasible ')
    sys.stdout.flush()

    rows = len(b_ub)
    cols = len(A_ub[0])

    progress = max(1, rows / 100)
    '''
    Delays should be in order of ns, so a 10 ns delay should be way above what anything should be
    Series can have several hundred delay elements
    Max delay in ballpark
    '''
    xs = [1e9 for _i in range(cols)]

    # FIXME: use the correct np function to do this for me
    # Verify bounds
    #b_res = np.matmul(A_ub, xs)
    #print(type(A_ub), type(xs)
    #A_ub = np.array(A_ub)
    #xs = np.array(xs)
    #b_res = np.matmul(A_ub, xs)
    def my_mul(A_ub, xs):
        #print('cols', cols
        #print('rows', rows
        ret = [None] * rows
        for row in range(rows):
            this = 0
            for col in range(cols):
                this += A_ub[row][col] * xs[col]
            ret[row] = this
        return ret

    b_res = my_mul(A_ub, xs)

    # Verify bound was respected
    for rowi, (this_b, this_b_ub) in enumerate(zip(b_res, b_ub)):
        if rowi % progress == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
        if this_b >= this_b_ub or this_b > 0:
            print(
                '% 4d Want res % 10.1f <= % 10.1f <= 0' %
                (rowi, this_b, this_b_ub))
            raise Exception("Bad ")
    print(' done')


def filter_bounds(Ads, b, bounds, corner):
    '''
    Given min variable delays, remove rows that won't constrain solution
       Ex for max corner:
    Given bounds:
        a >= 10
        b >= 1
        c >= 0
    Given equations:
        a + b >= 10
        a + c >= 100
    The first equation is already satisfied
    However, the second needs either an increase in a or an increase in c    '''

    if 'max' in corner:
        # Keep delays possibly larger than current bound
        def keep(row_b, est):
            return row_b > est

        T_UNK = 0
    elif 'min' in corner:
        # Keep delays possibly smaller than current bound
        def keep(row_b, est):
            return row_b < est

        T_UNK = 1e9
    else:
        assert 0

    ret_Ads = []
    ret_b = []
    unknowns = set()
    for row_ds, row_b in zip(Ads, b):
        # some variables get estimated at 0
        def getvar(k):
            #return bounds.get(k, T_UNK)
            ret = bounds.get(k, None)
            if ret is not None:
                return ret
            unknowns.add(k)
            return T_UNK

        est = sum([getvar(k) * v for k, v in row_ds.items()])
        # will this row potentially constrain us more?
        if keep(row_b, est):
            ret_Ads.append(row_ds)
            ret_b.append(row_b)
    if len(unknowns):
        print('WARNING: %u encountered undefined bounds' % len(unknowns))
    return ret_Ads, ret_b


def solve_save(outfn, xvals, names, corner, save_zero=True, verbose=False):
    # ballpark minimum actual observed delay is around 7 (carry chain)
    # anything less than one is probably a solver artifact
    delta = 0.5
    corneri = corner_s2i[corner]

    roundf = {
        'fast_max': math.ceil,
        'fast_min': math.floor,
        'slow_max': math.ceil,
        'slow_min': math.floor,
    }[corner]

    print('Writing results')
    zeros = 0
    with open(outfn, 'w') as fout:
        # write as one variable per line
        # this natively forms a bound if fed into linprog solver
        fout.write('ico,fast_max fast_min slow_max slow_min,rows...\n')
        for xval, name in zip(xvals, names):
            row_ico = 1

            if xval < delta:
                if verbose:
                    print('WARNING: near 0 delay on %s: %0.6f' % (name, xval))
                zeros += 1
                if not save_zero:
                    continue
            items = [str(row_ico), acorner2csv(roundf(xval), corneri)]
            items.append('%u %s' % (1, name))
            fout.write(','.join(items) + '\n')
    nonzeros = len(names) - zeros
    print(
        'Wrote: %u / %u constrained delays, %u zeros' %
        (nonzeros, len(names), zeros))
    assert nonzeros, 'Failed to estimate delay'


def run(
        fns_in,
        corner,
        run_corner,
        sub_json=None,
        bounds_csv=None,
        dedup=True,
        massage=False,
        outfn=None,
        verbose=False,
        **kwargs):
    print('Loading data')
    Ads, b = loadc_Ads_b(fns_in, corner)

    # Remove duplicate rows
    # is this necessary?
    # maybe better to just add them into the matrix directly
    if dedup:
        oldn = len(Ads)
        iold = instances(Ads)
        Ads, b = simplify_rows(Ads, b, corner=corner)
        print('Simplify %u => %u rows' % (oldn, len(Ads)))
        print('Simplify %u => %u instances' % (iold, instances(Ads)))

    if sub_json:
        print('Sub: %u rows' % len(Ads))
        iold = instances(Ads)
        names_old = index_names(Ads)
        run_sub_json(Ads, sub_json, verbose=verbose)
        names = index_names(Ads)
        print("Sub: %u => %u names" % (len(names_old), len(names)))
        print('Sub: %u => %u instances' % (iold, instances(Ads)))
    else:
        names = index_names(Ads)
    '''
    Substitution .csv
    Special .csv containing one variable per line
    Used primarily for multiple optimization passes, such as different algorithms or additional constraints
    '''
    if bounds_csv:
        Ads2, b2 = loadc_Ads_b([bounds_csv], corner)
        bounds = Ads2bounds(Ads2, b2)
        assert len(bounds), 'Failed to load bounds'
        rows_old = len(Ads)
        Ads, b = filter_bounds(Ads, b, bounds, corner)
        print(
            'Filter bounds: %s => %s + %s rows' %
            (rows_old, len(Ads), len(Ads2)))
        Ads = Ads + Ads2
        b = b + b2
        assert len(Ads) or allow_zero_eqns()
        assert len(Ads) == len(b), 'Ads, b length mismatch'

    if verbose:
        print
        print_eqns(Ads, b, verbose=verbose)

        #print
        #col_dist(A_ubd, 'final', names)
    if massage:
        try:
            Ads, b = massage_equations(Ads, b, corner=corner)
        except SimplifiedToZero:
            if not allow_zero_eqns():
                raise
            print('WARNING: simplified to zero equations')
            Ads = []
            b = []

    print('Converting to numpy...')
    names, Anp = A_ds2np(Ads)
    run_corner(
        Anp,
        np.asarray(b),
        names,
        corner,
        outfn=outfn,
        verbose=verbose,
        **kwargs)
