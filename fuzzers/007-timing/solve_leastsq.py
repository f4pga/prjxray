#!/usr/bin/env python3

# https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.optimize.linprog.html
from scipy.optimize import linprog
from timfuz import Benchmark, load_sub, corner_s2i, acorner2csv
import timfuz
import numpy as np
import glob
import math
from fractions import Fraction
import sys
import os
import time
import timfuz_solve
import scipy.optimize as optimize
from scipy.optimize import least_squares


def mkestimate(Anp, b):
    '''
    Ballpark upper bound estimate assuming variables contribute all of the delay in their respective row
    Return the min of all of the occurances

    XXX: should this be corner adjusted?
    '''
    cols = len(Anp[0])
    x0 = np.array([1e3 for _x in range(cols)])
    for row_np, row_b in zip(Anp, b):
        for coli, val in enumerate(row_np):
            if val:
                # Scale by number occurances
                ub = row_b / val
                if ub >= 0:
                    x0[coli] = min(x0[coli], ub)
    return x0


def save(outfn, xvals, names, corner):
    # ballpark minimum actual observed delay is around 7 (carry chain)
    # anything less than one is probably a solver artifact
    delta = 0.5
    corneri = corner_s2i[corner]

    # Round conservatively
    roundf = {
        'fast_max': math.ceil,
        'fast_min': math.floor,
        'slow_max': math.ceil,
        'slow_min': math.floor,
    }[corner]

    print('Writing results')
    skips = 0
    keeps = 0
    with open(outfn, 'w') as fout:
        # write as one variable per line
        # this natively forms a bound if fed into linprog solver
        fout.write('ico,fast_max fast_min slow_max slow_min,rows...\n')
        for xval, name in zip(xvals, names):
            row_ico = 1

            # also review ceil vs floor choice for min vs max
            # lets be more conservative for now
            if xval < delta:
                #print('Skipping %s: %0.6f' % (name, xval))
                skips += 1
                continue
            keeps += 1
            #xvali = round(xval)

            items = [str(row_ico), acorner2csv(roundf(xval), corneri)]
            items.append('%u %s' % (1, name))
            fout.write(','.join(items) + '\n')
    print(
        'Wrote: skip %u => %u / %u valid delays' % (skips, keeps, len(names)))
    assert keeps, 'Failed to estimate delay'


def run_corner(
        Anp, b, names, corner, verbose=False, opts={}, meta={}, outfn=None):
    # Given timing scores for above delays (-ps)
    assert type(Anp[0]) is np.ndarray, type(Anp[0])
    assert type(b) is np.ndarray, type(b)

    #check_feasible(Anp, b)
    '''
    Be mindful of signs
    Have something like
    timing1/timing 2 are constants
    delay1 +   delay2 +               delay4     >= timing1
               delay2 +   delay3                 >= timing2

    But need it in compliant form:
    -delay1 +   -delay2 +               -delay4     <= -timing1
                -delay2 +   -delay3                 <= -timing2
    '''
    rows = len(Anp)
    cols = len(Anp[0])

    print('Unique delay elements: %d' % len(names))
    print('Input paths')
    print('  # timing scores: %d' % len(b))
    print('  Rows: %d' % rows)
    '''
    You must have at least as many things to optimize as variables
    That is, the system must be plausibly constrained for it to attempt a solve
    If not, you'll get a message like
    TypeError: Improper input: N=3 must not exceed M=2
    '''
    if rows < cols:
        raise Exception("rows must be >= cols")

    tlast = [None]
    iters = [0]
    printn = [0]

    def progress_print():
        iters[0] += 1
        if tlast[0] is None:
            tlast[0] = time.time()
        if time.time() - tlast[0] > 1.0:
            sys.stdout.write('I:%d ' % iters[0])
            tlast[0] = time.time()
            printn[0] += 1
            if printn[0] % 10 == 0:
                sys.stdout.write('\n')
            sys.stdout.flush()

    def func(params):
        progress_print()
        return (b - np.dot(Anp, params))

    print('')
    # Now find smallest values for delay constants
    # Due to input bounds (ex: column limit), some delay elements may get eliminated entirely
    print('Running leastsq w/ %d r, %d c (%d name)' % (rows, cols, len(names)))
    # starting at 0 completes quicky, but gives a solution near 0 with terrible results
    # maybe give a starting estimate to the smallest net delay with the indicated variable
    #x0 = np.array([1000.0 for _x in range(cols)])
    print('Creating x0 estimate')
    x0 = mkestimate(Anp, b)

    print('Solving')
    res = least_squares(func, x0, bounds=(0, float('inf')))
    print('Done')

    if outfn:
        save(outfn, res.x, names, corner)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Solve timing solution using least squares objective function')

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--massage', action='store_true', help='')
    parser.add_argument(
        '--sub-json', help='Group substitutions to make fully ranked')
    parser.add_argument('--corner', default="slow_max", help='')
    parser.add_argument(
        '--out', default=None, help='output timing delay .json')
    parser.add_argument('fns_in', nargs='+', help='timing3.csv input files')
    args = parser.parse_args()
    # Store options in dict to ease passing through functions
    bench = Benchmark()

    sub_json = None
    if args.sub_json:
        sub_json = load_sub(args.sub_json)

    try:
        timfuz_solve.run(
            run_corner=run_corner,
            sub_json=sub_json,
            fns_in=args.fns_in,
            corner=args.corner,
            massage=args.massage,
            outfn=args.out,
            verbose=args.verbose)
    finally:
        print('Exiting after %s' % bench)


if __name__ == '__main__':
    main()
