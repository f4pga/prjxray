#!/usr/bin/env python3

# https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.optimize.linprog.html
from scipy.optimize import linprog
from timfuz import Benchmark, Ar_di2np, Ar_ds2t, A_di2ds, A_ds2di, simplify_rows, loadc_Ads_b, index_names, A_ds2np, load_sub, run_sub_json, A_ub_np2d, print_eqns, print_eqns_np
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

    # Chose a high arbitrary value for x
    # Delays should be in order of ns, so a 10 ns delay should be way above what anything should be
    xs = [10e3 for _i in range(cols)]

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
            print('% 4d Want res % 10.1f <= % 10.1f <= 0' % (rowi, this_b, this_b_ub))
            raise Exception("Bad ")
    print(' done')

def run_corner(Anp, b, names, verbose=False, opts={}, meta={}):
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
    print('Scaling to solution form...')
    b_ub = -1.0 * b
    #A_ub = -1.0 * Anp
    A_ub = [-1.0 * x for x in Anp]

    if verbose:
        print('')
        print('A_ub b_ub')
        print_eqns_np(A_ub, b_ub, verbose=verbose)
        print('')

    print('Creating misc constants...')
    # Minimization function scalars
    # Treat all logic elements as equally important
    c = [1 for _i in range(len(names))]
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
    print('Running linprog w/ %d r, %d c (%d name)' % (rows, cols, len(names)))
    res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, callback=callback,
          options={"disp": True, 'maxiter': maxiter, 'bland': True, 'tol': 1e-6,})
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
            if nonzero and (verbose or ((nonzeros < 100 or nonzeros % 20 == 0) and nonzeros <= plim)):
                print('  % 4u % -80s % 10.1f' % (xi, name, x))
        print('Delay on %d / %d' % (nonzeros, len(res.x)))
        if not os.path.exists('res'):
            os.mkdir('res')
        fn_out = 'res/%s' % datetime.datetime.utcnow().isoformat().split('.')[0]
        print('Writing %s' % fn_out)
        np.save(fn_out, (3, c, A_ub, b_ub, bounds, names, res, meta))

def run(fns_in, corner, sub_json=None, dedup=True, massage=False, verbose=False):
    Ads, b = loadc_Ads_b(fns_in, corner, ico=True)

    # Remove duplicate rows
    # is this necessary?
    # maybe better to just add them into the matrix directly
    if dedup:
        oldn = len(Ads)
        Ads, b = simplify_rows(Ads, b)
        print('Simplify %u => %u rows' % (oldn, len(Ads)))

    if sub_json:
        print('Sub: %u rows' % len(Ads))
        names_old = index_names(Ads)
        run_sub_json(Ads, sub_json, verbose=verbose)
        names = index_names(Ads)
        print("Sub: %u => %u names" % (len(names_old), len(names)))
    else:
        names = index_names(Ads)

    if verbose:
        print
        print_eqns(Ads, b, verbose=verbose)

        #print
        #col_dist(A_ubd, 'final', names)

    if massage:
        Ads, b = massage_equations(Ads, b)

    print('Converting to numpy...')
    names, Anp = A_ds2np(Ads)
    run_corner(Anp, np.asarray(b), names, verbose=verbose)

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Solve timing solution'
    )

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--massage', action='store_true', help='')
    parser.add_argument('--sub-json', help='Group substitutions to make fully ranked')
    parser.add_argument('--corner', default="slow_max", help='')
    parser.add_argument(
        'fns_in',
        nargs='*',
        help='timing3.csv input files')
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
        run(sub_json=sub_json,
            fns_in=fns_in, verbose=args.verbose, corner=args.corner, massage=args.massage)
    finally:
        print('Exiting after %s' % bench)

if __name__ == '__main__':
    main()
