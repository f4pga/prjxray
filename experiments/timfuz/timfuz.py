#!/usr/bin/env python

# https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.optimize.linprog.html
from scipy.optimize import linprog
import math
import numpy as np
from collections import OrderedDict
import time
import re
import os
import datetime
import json
import copy
import sys
import random
import glob

from benchmark import Benchmark

NAME_ZERO = set([
            "BSW_CLK_ZERO",
            "BSW_ZERO",
            "B_ZERO",
            "C_CLK_ZERO",
            "C_DSP_ZERO",
            "C_ZERO",
            "I_ZERO",
            "O_ZERO",
            "RC_ZERO",
            "R_ZERO",
            ])

# csv index
corner_s2i = {
    'fast_max': 0,
    'fast_min': 1,
    'slow_max': 2,
    'slow_min': 3,
    }

def print_eqns(A_ubd, b_ub, verbose=0, lim=3, label=''):
    rows = len(b_ub)

    print('Sample equations (%s) from %d r' % (label, rows))
    prints = 0
    #verbose = 1
    for rowi, row in enumerate(A_ubd):
        if verbose or ((rowi < 10 or rowi % max(1, (rows / 20)) == 0) and (not lim or prints < lim)):
            line = '  EQN: p%u: ' % rowi
            for k, v in sorted(row.items()):
                line += '%u*t%d ' % (v, k)
            line += '= %d' % b_ub[rowi]
            print(line)
            prints += 1

def print_name_eqns(A_ubd, b_ub, names, verbose=0, lim=3, label=''):
    rows = len(b_ub)

    print('Sample equations (%s) from %d r' % (label, rows))
    prints = 0
    #verbose = 1
    for rowi, row in enumerate(A_ubd):
        if verbose or ((rowi < 10 or rowi % max(1, (rows / 20)) == 0) and (not lim or prints < lim)):
            line = '  EQN: p%u: ' % rowi
            for k, v in sorted(row.items()):
                line += '%u*%s ' % (v, names[k])
            line += '= %d' % b_ub[rowi]
            print(line)
            prints += 1

def print_names(names, verbose=1):
    print('Names: %d' % len(names))
    for xi, name in enumerate(names):
        print('  % 4u % -80s' % (xi, name))

def invb(b_ub):
    #return [-b for b in b_ub]
    return -np.array(b_ub)

def check_feasible_d(A_ubd, b_ub, names):
    A_ub, b_ub_inv = Ab_d2np(A_ubd, b_ub, names)
    check_feasible(A_ub, b_ub_inv)

def check_feasible(A_ub, b_ub):
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

def Ab_ub_dt2d(eqns):
    '''Convert dict using the rows as keys into a list of dicts + b_ub list (ie return A_ub, b_ub)'''
    #return [dict(rowt) for rowt in eqns]
    rows = [(dict(rowt), b) for rowt, b in eqns.items()]
    A_ubd, b_ub = zip(*rows)
    return list(A_ubd), list(b_ub)

# This significantly reduces runtime
def simplify_rows(A_ubd, b_ub):
    '''Remove duplicate equations, taking highest delay'''
    # dict of constants to highest delay
    eqns = OrderedDict()
    assert len(A_ubd) == len(b_ub), (len(A_ubd), len(b_ub))

    sys.stdout.write('SimpR ')
    sys.stdout.flush()
    progress = max(1, len(b_ub) / 100)
    zero_ds = 0
    zero_es = 0
    for loopi, (b, rowd) in enumerate(zip(b_ub, A_ubd)):
        if loopi % progress == 0:
            sys.stdout.write('.')
            sys.stdout.flush()

        # TODO: elements have zero delay (ex: COUT)
        # Remove these from now since they make me nervous
        # Although they should just solve to 0
        if not b:
            zero_ds += 1
            continue

        # A very few of these exist with very small values
        # TODO: investigate, understand what these are
        # Leaving these in can make the result unsolvable since there does not exist a set of constants to reach the delay
        if len(rowd) == 0:
            zero_es += 1
            continue

        rowt = Ar_ds2t(rowd)
        eqns[rowt] = max(eqns.get(rowt, 0), b)

    print(' done')

    #A_ub_ret = eqns.keys()
    A_ubd_ret, b_ub_ret = Ab_ub_dt2d(eqns)

    print('Simplify rows: %d => %d w/ zd %d, ze %d' % (len(b_ub), len(b_ub_ret), zero_ds, zero_es))
    #return A_ub_ret, b_ub_ret
    #return A_ub_np2d(A_ub_ret), b_ub_ret
    return A_ubd_ret, b_ub_ret

def simplify_cols(names, A_ubd, b_ub):
    '''
    Remove unsued columns
    This is fairly straightforward in dictionary form now as only have to remove and adjust indices
    Maybe should use the names as keys? Then this wouldn't be needed anymore as indices wouldn't need to be rebased

    XXX: shuffles the name order around. Do we care?
    '''

    # First: find unused names
    # use dict since no standard ordered set
    used_cols = set()
    names_ret = OrderedDict()
    col_old2new = OrderedDict()
    rows = len(b_ub)
    cols = len(names)

    sys.stdout.write('SimpC indexing ')
    sys.stdout.flush()
    progress = max(1, rows / 100)
    for rowi, rowd in enumerate(A_ubd):
        if rowi % progress == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
        for coli in rowd.keys():
            used_cols.add(coli)

    for coli in range(cols):
        if coli in used_cols:
            names_ret[names[coli]] = None
            col_old2new[coli] = len(col_old2new)
    assert len(used_cols) == len(col_old2new)

    print(' done')

    # Create a new matrix, copying important values over
    #A_ub_ret = np.zeros((4, 1))
    #A_ub_ret[3][0] = 1.0
    #A_ub_ret = np.zeros((rows, len(names_ret)))
    A_ub_ret = [None] * rows
    sys.stdout.write('SimpC creating ')
    sys.stdout.flush()
    progress = max(1, rows / 100)
    for rowi, rowd_old in enumerate(A_ubd):
        if rowi % progress == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
        l = [(col_old2new[k], v) for k, v in rowd_old.items()]
        A_ub_ret[rowi] = OrderedDict(l)
    print(' done')

    print('Simplify cols: %d => %d cols' % (len(names), len(names_ret)))
    nr = list(names_ret.keys())
    return nr, A_ub_ret, b_ub

def A_ubr_np2d(row, sf=1):
    '''Convert a single row'''
    #d = {}
    d = OrderedDict()
    for coli, val in enumerate(row):
        if val:
            d[coli] = sf * val
    return d

def A_ub_np2d(A_ub, sf=1):
    '''Convert A_ub entries in numpy matrix to dictionary / sparse form'''
    A_ubd = [None] * len(A_ub)
    for i, row in enumerate(A_ub):
        A_ubd[i] = A_ubr_np2d(row, sf=sf)
    return A_ubd

# def Ar_ds2np(row_ds, names):
#     Ar_di2np(row_di, cols, sf=1)

def Ar_di2np(row_di, cols, sf=1):
    rownp = np.zeros(cols)
    for coli, val in row_di.items():
        # Sign inversion due to way solver works
        rownp[coli] = sf * val
    return rownp

# NOTE: sign inversion
def A_di2np(Adi, cols, sf=1):
    '''Convert A_ub entries in dictionary / sparse to numpy matrix form'''
    return [Ar_di2np(row_di, cols, sf=sf) for row_di in Adi]

def Ar_ds2t(rowd):
    '''Convert a dictionary row into a tuple with (column number, value) tuples'''
    return tuple(sorted(rowd.items()))

def A_ubr_t2d(rowt):
    '''Convert a dictionary row into a tuple with (column number, value) tuples'''
    return OrderedDict(rowt)

def A_ub_d2t(A_ubd):
    '''Convert rows as dicts to rows as tuples'''
    return [Ar_ds2t(rowd) for rowd in A_ubd]

def A_ub_t2d(A_ubd):
    '''Convert rows as tuples to rows as dicts'''
    return [OrderedDict(rowt) for rowt in A_ubd]

def Ab_d2np(A_ubd, b_ub, names):
    A_ub = A_di2np(A_ubd, len(names))
    b_ub_inv = invb(b_ub)
    return A_ub, b_ub_inv

def Ab_np2d(A_ub, b_ub_inv):
    A_ubd = A_ub_np2d(A_ub)
    b_ub = invb(b_ub_inv)
    return A_ubd, b_ub

def sort_equations_(A_ubd, b_ub):
    # Dictionaries aren't hashable for sorting even though they are comparable
    return A_ub_t2d(sorted(A_ub_d2t(A_ubd)))

def sort_equations(A_ub, b_ub):
    # Track rows with value column
    # Hmm can't sort against np arrays
    tosort = [(sorted(row.items()), b) for row, b in zip(A_ub, b_ub)]
    #res = sorted(tosort, key=lambda e: e[0])
    res = sorted(tosort)
    A_ubtr, b_ubr = zip(*res)
    return [OrderedDict(rowt) for rowt in A_ubtr], b_ubr

def lte_const(row_ref, row_cmp):
    '''Return true if all constants are smaller magnitude in row_cmp than row_ref'''
    #return False
    for k, vc in row_cmp.items():
        vr = row_ref.get(k, None)
        # Not in reference?
        if vr is None:
            return False
        if vr < vc:
            return False
    return True

def shared_const(row_ref, row_cmp):
    '''Return true if more constants are equal than not equal'''
    #return False
    matches = 0
    unmatches = 0
    ks = list(row_ref.keys()) + list(row_cmp.keys())
    for k in ks:
        vr = row_ref.get(k, None)
        vc = row_cmp.get(k, None)
        # At least one
        if vr is not None and vc is not None:
            if vc == vr:
                matches += 1
            else:
                unmatches += 1
        else:
            unmatches += 1

    # Will equation reduce if subtracted?
    return matches > unmatches

def reduce_const(row_ref, row_cmp):
    '''Subtract cmp constants from ref'''
    #ret = {}
    ret = OrderedDict()
    ks = set(row_ref.keys())
    ks.update(set(row_cmp.keys()))
    for k in ks:
        vr = row_ref.get(k, 0)
        vc = row_cmp.get(k, 0)
        res = vr - vc
        if res:
            ret[k] = res
    return ret

def derive_eq_by_row(A_ubd, b_ub, verbose=0, col_lim=0, tweak=False):
    '''
    Derive equations by subtracting whole rows

    Given equations like:
    t0           >= 10
    t0 + t1      >= 15
    t0 + t1 + t2 >= 17

    When I look at these, I think of a solution something like:
    t0 = 10f
    t1 = 5
    t2 = 2

    However, linprog tends to choose solutions like:
    t0 = 17
    t1 = 0
    t2 = 0

    To this end, add additional constraints by finding equations that are subsets of other equations
    How to do this in a reasonable time span?
    Also equations are sparse, which makes this harder to compute
    '''
    rows = len(A_ubd)
    assert rows == len(b_ub)

    # Index equations into hash maps so can lookup sparse elements quicker
    assert len(A_ubd) == len(b_ub)
    A_ubd_ret = copy.copy(A_ubd)
    assert len(A_ubd) == len(A_ubd_ret)

    #print('Finding subsets')
    ltes = 0
    scs = 0
    b_ub_ret = list(b_ub)
    sys.stdout.write('Deriving rows ')
    sys.stdout.flush()
    progress = max(1, rows / 100)
    for row_refi, row_ref in enumerate(A_ubd):
        if row_refi % progress == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
        if col_lim and len(row_ref) > col_lim:
            continue

        for row_cmpi, row_cmp in enumerate(A_ubd):
            if row_refi == row_cmpi or col_lim and len(row_cmp) > col_lim:
                continue
            # FIXME: this check was supposed to be removed
            '''
            Every elements in row_cmp is in row_ref
            but this doesn't mean the constants are smaller
            Filter these out
            '''
            # XXX: just reduce and filter out solutions with positive constants
            # or actually are these also useful as is?
            lte = lte_const(row_ref, row_cmp)
            if lte:
                ltes += 1
            sc = 0 and shared_const(row_ref, row_cmp)
            if sc:
                scs += 1
            if lte or sc:
                if verbose:
                    print('')
                    print('match')
                    print('  ', row_ref, b_ub[row_refi])
                    print('  ', row_cmp, b_ub[row_cmpi])
                # Reduce
                A_new = reduce_const(row_ref, row_cmp)
                # Did this actually significantly reduce the search space?
                #if tweak and len(A_new) > 4 and len(A_new) > len(row_cmp) / 2:
                if tweak and len(A_new) > 8 and len(A_new) > len(row_cmp) / 2:
                    continue
                b_new = b_ub[row_refi] - b_ub[row_cmpi]
                # Definitely possible
                # Maybe filter these out if they occur?
                if verbose:
                    print(b_new)
                # Also inverted sign
                if b_new <= 0:
                    if verbose:
                        print("Unexpected b")
                    continue
                if verbose:
                    print('OK')
                A_ubd_ret.append(A_new)
                b_ub_ret.append(b_new)
    print(' done')

    #A_ub_ret = A_di2np(A_ubd2, cols=cols)
    print('Derive row: %d => %d rows using %d lte, %d sc' % (len(b_ub), len(b_ub_ret), ltes, scs))
    assert len(A_ubd_ret) == len(b_ub_ret)
    return A_ubd_ret, b_ub_ret

def derive_eq_by_col(A_ubd, b_ub, verbose=0):
    '''
    Derive equations by subtracting out all bounded constants (ie "known" columns)
    '''
    rows = len(A_ubd)

    # Find all entries where

    # Index equations with a single constraint
    knowns = {}
    sys.stdout.write('Derive col indexing ')
    #A_ubd = A_ub_np2d(A_ub)
    sys.stdout.flush()
    progress = max(1, rows / 100)
    for row_refi, row_refd in enumerate(A_ubd):
        if row_refi % progress == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
        if len(row_refd) == 1:
            k, v = list(row_refd.items())[0]
            # Reduce any constants to canonical form
            if v != 1:
                row_refd[k] = 1
                b_ub[row_refi] /= v
            knowns[k] = b_ub[row_refi]
    print(' done')
    #knowns_set = set(knowns.keys())
    print('%d constrained' % len(knowns))

    '''
    Now see what we can do
    Rows that are already constrained: eliminate
        TODO: maybe keep these if this would violate their constraint
    Otherwise eliminate the original row and generate a simplified result now
    '''
    b_ub_ret = []
    A_ubd_ret = []
    sys.stdout.write('Derive col main ')
    sys.stdout.flush()
    progress = max(1, rows / 100)
    for row_refi, row_refd in enumerate(A_ubd):
        if row_refi % progress == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
        # Reduce as much as possible
        #row_new = {}
        row_new = OrderedDict()
        b_new = b_ub[row_refi]
        # Copy over single entries
        if len(row_refd) == 1:
            row_new = row_refd
        else:
            for k, v in row_refd.items():
                if k in knowns:
                    # Remove column and take out corresponding delay
                    b_new -= v * knowns[k]
                # Copy over
                else:
                    row_new[k] = v

        # Possibly reduced all usable contants out
        if len(row_new) == 0:
            continue
        if b_new <= 0:
            continue

        A_ubd_ret.append(row_new)
        b_ub_ret.append(b_new)
    print(' done')

    print('Derive col: %d => %d rows' % (len(b_ub), len(b_ub_ret)))
    return A_ubd_ret, b_ub_ret

def col_dist(A_ubd, desc='of', names=[], lim=0):
    '''print(frequency distribution of number of elements in a given row'''
    rows = len(A_ubd)
    cols = len(names)

    fs = {}
    for row in A_ubd:
        this_cols = len(row)
        fs[this_cols] = fs.get(this_cols, 0) + 1

    print('Col count distribution (%s) for %dr x %dc w/ %d freqs' % (desc, rows, cols, len(fs)))
    prints = 0
    for i, (k, v) in enumerate(sorted(fs.items())):
        if lim == 0 or (lim and prints < lim or i == len(fs) - 1):
            print('  %d: %d' % (k, v))
        prints += 1
        if lim and prints == lim:
            print('  ...')

def name_dist(A_ubd, desc='of', names=[], lim=0):
    '''print(frequency distribution of number of times an element appears'''
    rows = len(A_ubd)
    cols = len(names)

    fs = {i: 0 for i in range(len(names))}
    for row in A_ubd:
        for k in row.keys():
            fs[k] += 1

    print('Name count distribution (%s) for %dr x %dc' % (desc, rows, cols))
    prints = 0
    for namei, name in enumerate(names):
        if lim == 0 or (lim and prints < lim or namei == len(fs) - 1):
            print('  %s: %d' % (name, fs[namei]))
            prints += 1
            if lim and prints == lim:
                print('  ...')

    fs2 = {}
    for v in fs.values():
        fs2[v] = fs2.get(v, 0) + 1
    prints = 0
    print('Distribution distribution (%d items)'% len(fs2))
    for i, (k, v) in enumerate(sorted(fs2.items())):
        if lim == 0 or (lim and prints < lim or i == len(fs2) - 1):
            print('  %s: %s' % (k, v))
            prints += 1
            if lim and prints == lim:
                print('  ...')

    zeros = fs2.get(0, 0)
    if zeros:
        raise Exception("%d names without equation" % zeros)

def filter_ncols(A_ubd, b_ub, cols_min=0, cols_max=0):
    '''Only keep equations with a few delay elements'''
    A_ubd_ret = []
    b_ub_ret = []

    #print('Removing large rows')
    for rowd, b in zip(A_ubd, b_ub):
        if (not cols_min or len(rowd) >= cols_min) and (not cols_max or len(rowd) <= cols_max):
            A_ubd_ret.append(rowd)
            b_ub_ret.append(b)

    print('Filter ncols w/ %d <= cols <= %d: %d ==> %d rows' % (cols_min, cols_max, len(b_ub), len(b_ub_ret)))
    assert len(b_ub_ret)
    return A_ubd_ret, b_ub_ret

def preprocess(A_ubd, b_ub, opts, names, verbose=0):
    def debug(what):
        if verbose:
            print('')
            print_eqns(A_ubd, b_ub, verbose=verbose, label=what, lim=20)
            col_dist(A_ubd, what, names)
            check_feasible_d(A_ubd, b_ub, names)

    col_dist(A_ubd, 'pre-filt', names, lim=12)
    debug('pre-filt')

    need_simpc = 0

    # Input set may have redundant constraints
    A_ubd, b_ub = simplify_rows(A_ubd=A_ubd, b_ub=b_ub)
    debug("simp_rows")
    cols_min_pre = opts.get('cols_min_pre', None)
    cols_max_pre = opts.get('cols_max_pre', None)
    # Filter input based on number of columns
    if cols_min_pre or cols_max_pre:
        A_ubd, b_ub = filter_ncols(A_ubd=A_ubd, b_ub=b_ub, cols_min=cols_min_pre, cols_max=cols_max_pre)
        debug("filt_ncols")
        need_simpc = 1

    # Limit input rows, mostly for quick full run checks
    row_limit = opts.get('row_limit', None)
    if row_limit:
        before_rows = len(b_ub)
        A_ubd = A_ubd[0:row_limit]
        b_ub = b_ub[0:row_limit]
        print('Row limit %d => %d rows' % (before_rows, len(b_ub)))
        need_simpc = 1

    if need_simpc:
        names, A_ubd, b_ub = simplify_cols(names=names, A_ubd=A_ubd, b_ub=b_ub)
        debug("simp_cols")

    return A_ubd, b_ub, names

def massage_equations(A_ubd, b_ub, opts, names, verbose=0):
    '''
    Equation pipeline
    Some operations may generate new equations
    Simplify after these to avoid unnecessary overhead on redundant constraints
    Similarly some operations may eliminate equations, potentially eliminating a column (ie variable)
    Remove these columns as necessary to speed up solving
    '''

    def debug(what):
        if verbose:
            print('')
            print_eqns(A_ubd, b_ub, verbose=verbose, label=what, lim=20)
            col_dist(A_ubd, what, names)
            check_feasible_d(A_ubd, b_ub, names)

    A_ubd, b_ub, names = preprocess(A_ubd, b_ub, opts, names, verbose=verbose)

    # Try to (intelligently) subtract equations to generate additional constraints
    # This helps avoid putting all delay in a single shared variable
    derive_lim = opts.get('derive_lim', None)
    if derive_lim:
        dstart = len(b_ub)

        # Original simple
        if 0:
            for di in range(derive_lim):
                print
                assert len(A_ubd) == len(b_ub)
                n_orig = len(b_ub)

                # Meat of the operation
                # Focus on easy equations for first pass to get a lot of easy derrivations
                col_lim = 12 if di == 0 else None
                #col_lim = None
                A_ubd, b_ub = derive_eq_by_row(A_ubd, b_ub, col_lim=col_lim)
                debug("der_rows")
                # Run another simplify pass since new equations may have overlap with original
                A_ubd, b_ub = simplify_rows(A_ubd, b_ub)
                print('Derive row %d / %d: %d => %d equations' % (di + 1, derive_lim, n_orig, len(b_ub)))
                debug("der_rows simp")

                n_orig2 = len(b_ub)
                # Meat of the operation
                A_ubd, b_ub = derive_eq_by_col(A_ubd, b_ub)
                debug("der_cols")
                # Run another simplify pass since new equations may have overlap with original
                A_ubd, b_ub = simplify_rows(A_ubd=A_ubd, b_ub=b_ub)
                print('Derive col %d / %d: %d => %d equations' % (di + 1, derive_lim, n_orig2, len(b_ub)))
                debug("der_cols simp")

                if n_orig == len(b_ub):
                    break

        if 1:
            # Each iteration one more column is allowed until all columns are included
            # (and the system is stable)
            col_lim = 15
            di = 0
            while True:
                print
                n_orig = len(b_ub)

                print('Loop %d, lim %d' % (di + 1, col_lim))
                # Meat of the operation
                A_ubd, b_ub = derive_eq_by_row(A_ubd, b_ub, col_lim=col_lim, tweak=True)
                debug("der_rows")
                # Run another simplify pass since new equations may have overlap with original
                A_ubd, b_ub = simplify_rows(A_ubd, b_ub)
                print('Derive row: %d => %d equations' % (n_orig, len(b_ub)))
                debug("der_rows simp")

                n_orig2 = len(b_ub)
                # Meat of the operation
                A_ubd, b_ub = derive_eq_by_col(A_ubd, b_ub)
                debug("der_cols")
                # Run another simplify pass since new equations may have overlap with original
                A_ubd, b_ub = simplify_rows(A_ubd=A_ubd, b_ub=b_ub)
                print('Derive col %d: %d => %d equations' % (di + 1, n_orig2, len(b_ub)))
                debug("der_cols simp")

                # Doesn't help computation, but helps debugging
                names, A_ubd, b_ub = simplify_cols(names=names, A_ubd=A_ubd, b_ub=b_ub)
                A_ubd, b_ub = sort_equations(A_ubd, b_ub)
                debug("loop done")
                col_dist(A_ubd, 'derive done iter %d, lim %d' % (di, col_lim), names, lim=12)

                rows = len(A_ubd)
                if n_orig == len(b_ub) and col_lim >= rows:
                    break
                col_lim += col_lim / 5
                di += 1

        dend = len(b_ub)
        print('')
        print('Derive net: %d => %d' % (dstart, dend))
        print('')
        # Was experimentting to see how much the higher order columns really help

    cols_min_post = opts.get('cols_min_post', None)
    cols_max_post = opts.get('cols_max_post', None)
    # Filter input based on number of columns
    if cols_min_post or cols_max_post:
        A_ubd, b_ub = filter_ncols(A_ubd=A_ubd, b_ub=b_ub, cols_min=cols_min_post, cols_max=cols_max_post)
        debug("filter_ncals final")

    names, A_ubd, b_ub = simplify_cols(names=names, A_ubd=A_ubd, b_ub=b_ub)
    debug("simp_cols final")

    # Helps debug readability
    A_ubd, b_ub = sort_equations(A_ubd, b_ub)
    debug("final (sorted)")
    return names, A_ubd, b_ub

def Ar_di2ds(rowA, names):
    row = OrderedDict()
    for k, v in rowA.items():
        row[names[k]] = v
    return row

def A_di2ds(Adi, names):
    rows = []
    for row_di in Adi:
        rows.append(Ar_di2ds(row_di, names))
    return rows

def Ar_ds2di(row_ds, names):
    def keyi(name):
        if name not in names:
            names[name] = len(names)
        return names[name]

    row_di = OrderedDict()
    for k, v in row_ds.items():
        row_di[keyi(k)] = v
    return row_di

def A_ds2di(rows):
    names = OrderedDict()

    A_ubd = []
    for row_ds in rows:
        A_ubd.append(Ar_ds2di(row_ds, names))

    return list(names.keys()), A_ubd

def A_ds2np(Ads):
    names, Adi = A_ds2di(Ads)
    return names, A_di2np(Adi, len(names))

def loadc_Ads_mkb(fns, mkb, filt):
    bs = []
    Ads = []
    for fn in fns:
        with open(fn, 'r') as f:
            # skip header
            f.readline()
            for l in f:
                cols = l.split(',')
                ico = bool(int(cols[0]))
                corners = cols[1]
                vars = cols[2:]

                corners = [int(x) for x in corners.split()]
                def mkvar(x):
                    i, var = x.split()
                    return (var, int(i))
                vars = OrderedDict([mkvar(var) for var in vars])
                if not filt(ico, corners, vars):
                    continue

                bs.append(mkb(corners))
                Ads.append(vars)

    return Ads, bs

def loadc_Ads_b(fns, corner, ico=None):
    corner = corner or "slow_max"
    corneri = corner_s2i[corner]

    if ico is not None:
        filt = lambda ico, corners, vars: ico == ico
    else:
        filt = lambda ico, corners, vars: True

    def mkb(val):
        return val[corneri]
    return loadc_Ads_mkb(fns, mkb, filt)

def index_names(Ads):
    names = set()
    for row_ds in Ads:
        for k1 in row_ds.keys():
            names.add(k1)
    return names
