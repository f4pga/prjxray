#!/usr/bin/env python3

import scipy.optimize as optimize
import numpy as np
import glob
import json
import math
import sys
import os
import time


def run_max(Anp, b, verbose=False):
    cols = len(Anp[0])

    b_ub = -1.0 * b
    A_ub = [-1.0 * x for x in Anp]

    res = optimize.linprog(
        c=[1 for _i in range(cols)],
        A_ub=A_ub,
        b_ub=b_ub,
        bounds=(0, None),
        options={
            "disp": True,
            'maxiter': 1000000,
            'bland': True,
            'tol': 1e-6,
        })
    nonzeros = 0
    print('Ran')
    if res.success:
        print('Result sample (%d elements)' % (len(res.x)))
        plim = 3
        for xi, x in enumerate(res.x):
            nonzero = x >= 0.001
            if nonzero:
                nonzeros += 1
            if nonzero and (verbose or (
                (nonzeros < 100 or nonzeros % 20 == 0) and nonzeros <= plim)):
                print('  % 4u  % 10.1f' % (xi, x))
        print('Delay on %d / %d' % (nonzeros, len(res.x)))


def run_min(Anp, b, verbose=False):
    cols = len(Anp[0])

    b_ub = b
    A_ub = Anp

    res = optimize.linprog(
        c=[-1 for _i in range(cols)],
        A_ub=A_ub,
        b_ub=b_ub,
        bounds=(0, None),
        options={
            "disp": True,
            'maxiter': 1000000,
            'bland': True,
            'tol': 1e-6,
        })
    nonzeros = 0
    print('Ran')
    if res.success:
        print('Result sample (%d elements)' % (len(res.x)))
        plim = 3
        for xi, x in enumerate(res.x):
            nonzero = x >= 0.001
            if nonzero:
                nonzeros += 1
            if nonzero and (verbose or (
                (nonzeros < 100 or nonzeros % 20 == 0) and nonzeros <= plim)):
                print('  % 4u  % 10.1f' % (xi, x))
        print('Delay on %d / %d' % (nonzeros, len(res.x)))


def run(verbose=False):
    '''
    1 * x0          =  10
    1 * x0 + 1 * x1 = 100
    1 * x0          =  40
             2 * x1 = 140
    '''
    Anp = np.array([
        [1, 0],
        [1, 1],
        [1, 0],
        [0, 2],
    ])
    b = np.array([
        10,
        100,
        40,
        140,
    ])
    '''
    Max
    Optimization terminated successfully.
             Current function value: 110.000000  
             Iterations: 4
    Ran
    Result sample (2 elements)
         0        40.0
         1        70.0
    Delay on 2 / 2
    '''
    print('Max')
    run_max(Anp, b)
    print('')
    print('')
    print('')
    '''
    Min
    Optimization terminated successfully.
             Current function value: -80.000000  
             Iterations: 2
    Ran
    Result sample (2 elements)
         0        10.0
         1        70.0
    Delay on 2 / 2
    '''
    print('Min')
    run_min(Anp, b)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Test')

    parser.add_argument('--verbose', action='store_true', help='')
    args = parser.parse_args()

    run(verbose=args.verbose)


if __name__ == '__main__':
    main()
