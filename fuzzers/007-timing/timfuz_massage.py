#!/usr/bin/env python3

from timfuz import simplify_rows, print_eqns, print_eqns_np, sort_equations, col_dist, index_names
import numpy as np
import math
import sys
import datetime
import os
import time
import copy
from collections import OrderedDict


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


def derive_eq_by_row(Ads, b, verbose=0, col_lim=0, tweak=False):
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
    assert len(Ads) == len(b), 'Ads, b length mismatch'
    rows = len(Ads)

    # Index equations into hash maps so can lookup sparse elements quicker
    assert len(Ads) == len(b)
    Ads_ret = copy.copy(Ads)
    assert len(Ads) == len(Ads_ret)

    #print('Finding subsets')
    ltes = 0
    scs = 0
    b_ret = list(b)
    sys.stdout.write('Deriving rows (%u) ' % rows)
    sys.stdout.flush()
    progress = int(max(1, rows / 100))
    for row_refi, row_ref in enumerate(Ads):
        if row_refi % progress == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
        if col_lim and len(row_ref) > col_lim:
            continue

        for row_cmpi, row_cmp in enumerate(Ads):
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
                    print('  ', row_ref, b[row_refi])
                    print('  ', row_cmp, b[row_cmpi])
                # Reduce
                A_new = reduce_const(row_ref, row_cmp)
                # Did this actually significantly reduce the search space?
                #if tweak and len(A_new) > 4 and len(A_new) > len(row_cmp) / 2:
                if tweak and len(A_new) > 8 and len(A_new) > len(row_cmp) / 2:
                    continue
                b_new = b[row_refi] - b[row_cmpi]
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
                Ads_ret.append(A_new)
                b_ret.append(b_new)
    print(' done')

    #A_ub_ret = A_di2np(Ads2, cols=cols)
    print(
        'Derive row: %d => %d rows using %d lte, %d sc' %
        (len(b), len(b_ret), ltes, scs))
    assert len(Ads_ret) == len(b_ret)
    return Ads_ret, b_ret


def derive_eq_by_near_row(Ads, b, verbose=0, col_lim=0, tweak=False):
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
    rows = len(Ads)
    assert rows == len(b)
    rowdelta = int(rows / 2)

    # Index equations into hash maps so can lookup sparse elements quicker
    assert len(Ads) == len(b)
    Ads_ret = copy.copy(Ads)
    assert len(Ads) == len(Ads_ret)

    #print('Finding subsets')
    ltes = 0
    scs = 0
    b_ret = list(b)
    sys.stdout.write('Deriving rows (%u) ' % rows)
    sys.stdout.flush()
    progress = int(max(1, rows / 100))
    for row_refi, row_ref in enumerate(Ads):
        if row_refi % progress == 0:
            sys.stdout.write('.')
            sys.stdout.flush()
        if col_lim and len(row_ref) > col_lim:
            continue

        #for row_cmpi, row_cmp in enumerate(Ads):
        for row_cmpi in range(max(0, row_refi - rowdelta),
                              min(len(Ads), row_refi + rowdelta)):
            if row_refi == row_cmpi or col_lim and len(row_cmp) > col_lim:
                continue
            row_cmp = Ads[row_cmpi]
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
                    print('  ', row_ref, b[row_refi])
                    print('  ', row_cmp, b[row_cmpi])
                # Reduce
                A_new = reduce_const(row_ref, row_cmp)
                # Did this actually significantly reduce the search space?
                #if tweak and len(A_new) > 4 and len(A_new) > len(row_cmp) / 2:
                #if tweak and len(A_new) > 8 and len(A_new) > len(row_cmp) / 2:
                #    continue
                b_new = b[row_refi] - b[row_cmpi]
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
                Ads_ret.append(A_new)
                b_ret.append(b_new)
    print(' done')

    #A_ub_ret = A_di2np(Ads2, cols=cols)
    print(
        'Derive row: %d => %d rows using %d lte, %d sc' %
        (len(b), len(b_ret), ltes, scs))
    assert len(Ads_ret) == len(b_ret)
    return Ads_ret, b_ret


def derive_eq_by_col(Ads, b_ub, verbose=0):
    '''
    Derive equations by subtracting out all bounded constants (ie "known" columns)
    '''
    rows = len(Ads)

    # Find all entries where

    # Index equations with a single constraint
    knowns = {}
    sys.stdout.write('Derive col indexing ')
    sys.stdout.flush()
    progress = max(1, rows / 100)
    for row_refi, row_refd in enumerate(Ads):
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
    b_ret = []
    Ads_ret = []
    sys.stdout.write('Derive col main ')
    sys.stdout.flush()
    progress = max(1, rows / 100)
    for row_refi, row_refd in enumerate(Ads):
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

        Ads_ret.append(row_new)
        b_ret.append(b_new)
    print(' done')

    print('Derive col: %d => %d rows' % (len(b_ub), len(b_ret)))
    return Ads_ret, b_ret


# iteratively increasing column limit until all columns are added
def massage_equations(Ads, b, verbose=False, corner=None):
    '''
    Subtract equations from each other to generate additional constraints
    Helps provide additional guidance to solver for realistic delays

    Equation pipeline
    Some operations may generate new equations
    Simplify after these to avoid unnecessary overhead on redundant constraints
    Similarly some operations may eliminate equations, potentially eliminating a column (ie variable)
    Remove these columns as necessary to speed up solving
    '''

    assert len(Ads) == len(b), 'Ads, b length mismatch'

    def debug(what):
        if verbose:
            print('')
            print_eqns(Ads, b, verbose=verbose, label=what, lim=20)
            col_dist(Ads, what)
            check_feasible_d(Ads, b)

    # Try to (intelligently) subtract equations to generate additional constraints
    # This helps avoid putting all delay in a single shared variable
    dstart = len(b)
    cols = len(index_names(Ads))

    # Each iteration one more column is allowed until all columns are included
    # (and the system is stable)
    col_lim = 15
    di = 0
    while True:
        print
        n_orig = len(b)

        print('Loop %d, lim %d' % (di + 1, col_lim))
        # Meat of the operation
        Ads, b = derive_eq_by_row(Ads, b, col_lim=col_lim, tweak=True)
        debug("der_rows")
        # Run another simplify pass since new equations may have overlap with original
        Ads, b = simplify_rows(Ads, b, corner=corner)
        print('Derive row: %d => %d equations' % (n_orig, len(b)))
        debug("der_rows simp")

        n_orig2 = len(b)
        # Meat of the operation
        Ads, b = derive_eq_by_col(Ads, b)
        debug("der_cols")
        # Run another simplify pass since new equations may have overlap with original
        Ads, b = simplify_rows(Ads, b, corner=corner)
        print('Derive col %d: %d => %d equations' % (di + 1, n_orig2, len(b)))
        debug("der_cols simp")

        # Doesn't help computation, but helps debugging
        Ads, b = sort_equations(Ads, b)
        debug("loop done")
        col_dist(Ads, 'derive done iter %d, lim %d' % (di, col_lim), lim=12)

        rows = len(Ads)
        # possible that a new equation was generated and taken away, but close enough
        if n_orig == len(b) and col_lim >= cols:
            break
        col_lim += col_lim / 5
        di += 1

        dend = len(b)
        print('')
        print('Derive net: %d => %d' % (dstart, dend))
        print('')
        # Was experimentting to see how much the higher order columns really help

    # Helps debug readability
    Ads, b = sort_equations(Ads, b)
    debug("final (sorted)")
    print('')
    print('Massage final: %d => %d rows' % (dstart, dend))
    return Ads, b
