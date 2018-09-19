#!/usr/bin/env python3

import scipy.optimize as optimize
from timfuz import Benchmark, load_sub, A_ub_np2d, acorner2csv, corner_s2i
import numpy as np
import glob
import json
import math
import sys
import os
import time
import timfuz_solve


def save(outfn, xvals, names, corner):
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

            # FIXME: only report for the given corner?
            # also review ceil vs floor choice for min vs max
            # lets be more conservative for now
            if xval < delta:
                print('WARNING: near 0 delay on %s: %0.6f' % (name, xval))
                zeros += 1
                #continue
            items = [str(row_ico), acorner2csv(roundf(xval), corneri)]
            items.append('%u %s' % (1, name))
            fout.write(','.join(items) + '\n')
    nonzeros = len(names) - zeros
    print(
        'Wrote: %u / %u constrained delays, %u zeros' %
        (nonzeros, len(names), zeros))


def run_corner(
        Anp, b, names, corner, verbose=False, opts={}, meta={}, outfn=None):
    if len(Anp) == 0:
        print('WARNING: zero equations')
        if outfn:
            save(outfn, [], [], corner)
        return
    maxcorner = {
        'slow_max': True,
        'slow_min': False,
        'fast_max': True,
        'fast_min': False,
    }[corner]

    # Given timing scores for above delays (-ps)
    assert type(Anp[0]) is np.ndarray, type(Anp[0])
    assert type(b) is np.ndarray, type(b)

    #check_feasible(Anp, b)
    '''
    Be mindful of signs
    t1, t2: total delay contants
    d1, d2..: variables to solve for

    Max corner intuitive form:
    d1 + d2 +     d4 >= t1
         d2 + d3     >= t2

    But need it in compliant form:
    -d1 + -d2 +      -d4 <= -t1
          -d2 + -d3      <= -t2
    Minimize delay elements


    Min corner intuitive form:
    d1 + d2 +     d4 <= t1
         d2 + d3     <= t2
    Maximize delay elements
    '''

    rows = len(Anp)
    cols = len(Anp[0])
    if maxcorner:
        print('maxcorner => scaling to solution form...')
        b_ub = -1.0 * b
        #A_ub = -1.0 * Anp
        A_ub = [-1.0 * x for x in Anp]
    else:
        print('mincorner => no scaling required')
        b_ub = b
        A_ub = Anp

    print('Creating misc constants...')
    # Minimization function scalars
    # Treat all logic elements as equally important
    if maxcorner:
        # Best result are min delays
        c = [1 for _i in range(len(names))]
    else:
        # Best result are max delays
        c = [-1 for _i in range(len(names))]
    # Delays cannot be negative
    # (this is also the default constraint)
    #bounds =  [(0, None) for _i in range(len(names))]
    # Also you can provide one to apply to all
    bounds = (0, None)

    # Seems to take about rows + 3 iterations
    # Give some margin
    #maxiter = int(1.1 * rows + 100)
    #maxiter = max(1000, int(1000 * rows + 1000))
    # Most of the time I want it to just keep going unless I ^C it
    maxiter = 1000000

    if verbose >= 2:
        print('b_ub', b)
    print('Unique delay elements: %d' % len(names))
    print('  # delay minimization weights: %d' % len(c))
    print('  # delay constraints: %d' % len(bounds))
    print('Input paths')
    print('  # timing scores: %d' % len(b))
    print('  Rows: %d' % rows)

    tlast = [time.time()]
    iters = [0]
    printn = [0]

    def callback(xk, **kwargs):
        iters[0] = kwargs['nit']
        if time.time() - tlast[0] > 1.0:
            sys.stdout.write('I:%d ' % kwargs['nit'])
            tlast[0] = time.time()
            printn[0] += 1
            if printn[0] % 10 == 0:
                sys.stdout.write('\n')
            sys.stdout.flush()

    print('')
    # Now find smallest values for delay constants
    # Due to input bounds (ex: column limit), some delay elements may get eliminated entirely
    # https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.optimize.linprog.html
    print('Running linprog w/ %d r, %d c (%d name)' % (rows, cols, len(names)))
    res = optimize.linprog(
        c,
        A_ub=A_ub,
        b_ub=b_ub,
        bounds=bounds,
        callback=callback,
        options={
            "disp": True,
            'maxiter': maxiter,
            'bland': True,
            'tol': 1e-6,
        })
    nonzeros = 0
    print('Ran %d iters' % iters[0])
    if res.success:
        print('Result sample (%d elements)' % (len(res.x)))
        plim = 3
        for xi, (name, x) in enumerate(zip(names, res.x)):
            nonzero = x >= 0.001
            if nonzero:
                nonzeros += 1
            #if nonzero and (verbose >= 1 or xi > 30):
            if nonzero and (verbose or (
                (nonzeros < 100 or nonzeros % 20 == 0) and nonzeros <= plim)):
                print('  % 4u % -80s % 10.1f' % (xi, name, x))
        print('Delay on %d / %d' % (nonzeros, len(res.x)))

        if outfn:
            save(outfn, res.x, names, corner)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Solve timing solution using linear programming inequalities')

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--massage', action='store_true', help='')
    parser.add_argument(
        '--bounds-csv', help='Previous solve result starting point')
    parser.add_argument(
        '--sub-json', help='Group substitutions to make fully ranked')
    parser.add_argument('--corner', required=True, default="slow_max", help='')
    parser.add_argument(
        '--out', default=None, help='output timing delay .json')
    parser.add_argument('fns_in', nargs='+', help='timing3.csv input files')
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
        timfuz_solve.run(
            run_corner=run_corner,
            sub_json=sub_json,
            bounds_csv=args.bounds_csv,
            fns_in=fns_in,
            corner=args.corner,
            massage=args.massage,
            outfn=args.out,
            verbose=args.verbose)
    finally:
        print('Exiting after %s' % bench)


if __name__ == '__main__':
    main()
