#!/usr/bin/env python

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
from fractions import Fraction
import collections

from benchmark import Benchmark


# Equations are filtered out until nothing is left
class SimplifiedToZero(Exception):
    pass


# http://code.activestate.com/recipes/576694/
class OrderedSet(collections.MutableSet):
    def __init__(self, iterable=None):
        self.end = end = []
        end += [None, end, end]  # sentinel node for doubly linked list
        self.map = {}  # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__, )
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)


NAME_ZERO = OrderedSet(
    [
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
corner_s2i = OrderedDict(
    [
        ('fast_max', 0),
        ('fast_min', 1),
        ('slow_max', 2),
        ('slow_min', 3),
    ])


def allow_zero_eqns():
    '''If true, allow a system of equations with no equations'''
    return os.getenv('ALLOW_ZERO_EQN', 'N') == 'Y'


def print_eqns(A_ubd, b_ub, verbose=0, lim=3, label=''):
    rows = len(b_ub)

    print('Sample equations (%s) from %d r' % (label, rows))
    prints = 0
    #verbose = 1
    for rowi, row in enumerate(A_ubd):
        if verbose or ((rowi < 10 or rowi % max(1, (rows / 20)) == 0) and
                       (not lim or prints < lim)):
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
        if verbose or ((rowi < 10 or rowi % max(1, (rows / 20)) == 0) and
                       (not lim or prints < lim)):
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
            print(
                '% 4d Want res % 10.1f <= % 10.1f <= 0' %
                (rowi, this_b, this_b_ub))
            raise Exception("Bad ")
    print(' done')


def Ab_ub_dt2d(eqns):
    '''Convert dict using the rows as keys into a list of dicts + b_ub list (ie return A_ub, b_ub)'''
    #return [dict(rowt) for rowt in eqns]
    rows = [(OrderedDict(rowt), b) for rowt, b in eqns.items()]
    A_ubd, b_ub = zip(*rows)
    return list(A_ubd), list(b_ub)


# This significantly reduces runtime
def simplify_rows(Ads, b_ub, remove_zd=False, corner=None):
    '''Remove duplicate equations, taking highest delay'''
    # dict of constants to highest delay
    eqns = OrderedDict()
    assert len(Ads) == len(b_ub), (len(Ads), len(b_ub))

    assert corner is not None
    minmax = {
        'fast_max': max,
        'fast_min': min,
        'slow_max': max,
        'slow_min': min,
    }[corner]
    # An outlier to make unknown values be ignored
    T_UNK = {
        'fast_max': 0,
        'fast_min': 10e9,
        'slow_max': 0,
        'slow_min': 10e9,
    }[corner]

    sys.stdout.write('SimpR ')
    sys.stdout.flush()
    progress = int(max(1, len(b_ub) / 100))
    zero_ds = 0
    zero_es = 0
    for loopi, (b, rowd) in enumerate(zip(b_ub, Ads)):
        if loopi % progress == 0:
            sys.stdout.write('.')
            sys.stdout.flush()

        # TODO: elements have zero delay (ex: COUT)
        # Remove these from now since they make me nervous
        # Although they should just solve to 0
        if remove_zd and not b:
            zero_ds += 1
            continue

        # think ran into these before when taking out ZERO elements
        if len(rowd) == 0:
            if b != 0:
                assert zero_es == 0, 'Unexpected zero element row with non-zero delay'
            zero_es += 1
            continue

        rowt = Ar_ds2t(rowd)
        eqns[rowt] = minmax(eqns.get(rowt, T_UNK), b)

    print(' done')

    print(
        'Simplify rows: %d => %d rows w/ zd %d, ze %d' %
        (len(b_ub), len(eqns), zero_ds, zero_es))
    if len(eqns) == 0:
        raise SimplifiedToZero()
    A_ubd_ret, b_ub_ret = Ab_ub_dt2d(eqns)
    return A_ubd_ret, b_ub_ret


def A_ubr_np2d(row):
    '''Convert a single row'''
    #d = {}
    d = OrderedDict()
    for coli, val in enumerate(row):
        if val:
            d[coli] = val
    return d


def A_ub_np2d(A_ub):
    '''Convert A_ub entries in numpy matrix to dictionary / sparse form'''
    Adi = [None] * len(A_ub)
    for i, row in enumerate(A_ub):
        Adi[i] = A_ubr_np2d(row)
    return Adi


def Ar_di2np(row_di, cols):
    rownp = np.zeros(cols)
    for coli, val in row_di.items():
        # Sign inversion due to way solver works
        rownp[coli] = val
    return rownp


# NOTE: sign inversion
def A_di2np(Adi, cols):
    '''Convert A_ub entries in dictionary / sparse to numpy matrix form'''
    return [Ar_di2np(row_di, cols) for row_di in Adi]


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


def sort_equations(Ads, b):
    # Track rows with value column
    # Hmm can't sort against np arrays
    tosort = [(sorted(row.items()), rowb) for row, rowb in zip(Ads, b)]
    #res = sorted(tosort, key=lambda e: e[0])
    res = sorted(tosort)
    A_ubtr, b_ubr = zip(*res)
    return [OrderedDict(rowt) for rowt in A_ubtr], b_ubr


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
    print(
        'Derive row: %d => %d rows using %d lte, %d sc' %
        (len(b_ub), len(b_ub_ret), ltes, scs))
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
    #knowns_set = OrderedSet(knowns.keys())
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


def col_dist(Ads, desc='of', names=[], lim=0):
    '''print(frequency distribution of number of elements in a given row'''
    rows = len(Ads)
    cols = len(names)

    fs = {}
    for row in Ads:
        this_cols = len(row)
        fs[this_cols] = fs.get(this_cols, 0) + 1

    print(
        'Col count distribution (%s) for %dr x %dc w/ %d freqs' %
        (desc, rows, cols, len(fs)))
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
    print('Distribution distribution (%d items)' % len(fs2))
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
        if (not cols_min or len(rowd) >= cols_min) and (not cols_max or
                                                        len(rowd) <= cols_max):
            A_ubd_ret.append(rowd)
            b_ub_ret.append(b)

    print(
        'Filter ncols w/ %d <= cols <= %d: %d ==> %d rows' %
        (cols_min, cols_max, len(b_ub), len(b_ub_ret)))
    assert len(b_ub_ret)
    return A_ubd_ret, b_ub_ret


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

                def mkcorner(bstr):
                    if bstr == 'None':
                        return None
                    else:
                        return int(bstr)

                corners = [mkcorner(corner) for corner in corners.split()]

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
        filt = lambda ico_, corners, vars: ico_ == ico
    else:
        filt = lambda ico_, corners, vars: True

    def mkb(val):
        return val[corneri]

    return loadc_Ads_mkb(fns, mkb, filt)


def loadc_Ads_bs(fns, ico=None):
    if ico is not None:
        filt = lambda ico_, corners, vars: ico_ == ico
    else:
        filt = lambda ico_, corners, vars: True

    def mkb(val):
        return val

    return loadc_Ads_mkb(fns, mkb, filt)


def loadc_Ads_raw(fns):
    filt = lambda ico, corners, vars: True

    def mkb(val):
        return val

    return loadc_Ads_mkb(fns, mkb, filt)


def index_names(Ads):
    names = OrderedSet()
    for row_ds in Ads:
        for k1 in row_ds.keys():
            names.add(k1)
    return names


def load_sub(fn):
    j = json.load(open(fn, 'r'))

    for name, vals in sorted(j['subs'].items()):
        for k, v in vals.items():
            vals[k] = Fraction(v[0], v[1])

    return j


def row_sub_vars(row, sub_json, strict=False, verbose=False):
    if 0 and verbose:
        print("")
        print(row.items())

    delvars = 0
    for k in sub_json['zero_names']:
        try:
            del row[k]
            delvars += 1
        except KeyError:
            pass
    if verbose:
        print("Deleted %u variables" % delvars)

    if verbose:
        print('Checking pivots')
        print(sorted(row.items()))
        for group, pivot in sorted(sub_json['pivots'].items()):
            if pivot not in row:
                continue
            n = row[pivot]
            print('  pivot %u %s' % (n, pivot))

    #pivots = set(sub_json['pivots'].values()).intersection(row.keys())
    for group, pivot in sorted(sub_json['pivots'].items()):
        if pivot not in row:
            continue
        # take the sub out n times
        # note constants may be negative
        n = row[pivot]
        if verbose:
            print('pivot %i %s' % (n, pivot))
        for subk, subv in sorted(sub_json['subs'][group].items()):
            oldn = row.get(subk, type(subv)(0))
            rown = -n * subv
            rown += oldn
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
    # numeric precision issues previously limited this
    # Ex: AssertionError: ('PIP_BSW_2ELSING0', -2.220446049250313e-16)
    if strict:
        # verify no subs are left
        for subs in sub_json['subs'].values():
            for sub in subs:
                assert sub not in row, 'non-pivot element after group sub %s' % sub

        # Verify all constants are positive
        for k, v in sorted(row.items()):
            assert v > 0, (k, v)


def run_sub_json(Ads, sub_json, strict=False, verbose=False):
    '''
    strict: complain if a sub doesn't go in evenly
    '''

    nrows = 0
    nsubs = 0

    ncols_old = 0
    ncols_new = 0

    print('Subbing %u rows' % len(Ads))
    prints = OrderedSet()

    for rowi, row in enumerate(Ads):
        if 0 and verbose:
            print(row)
        if verbose:
            print('')
            print('Row %u w/ %u elements' % (rowi, len(row)))

        row_orig = dict(row)
        row_sub_vars(row, sub_json, strict=strict, verbose=verbose)
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
    print("Sub: %u => %u non-zero row cols" % (ncols_old, ncols_new))


def print_eqns(Ads, b, verbose=0, lim=3, label=''):
    rows = len(b)

    print('Sample equations (%s) from %d r' % (label, rows))
    prints = 0
    for rowi, row in enumerate(Ads):
        if verbose or ((rowi < 10 or rowi % max(1, (rows / 20)) == 0) and
                       (not lim or prints < lim)):
            line = '  EQN: p%u: ' % rowi
            for k, v in sorted(row.items()):
                line += '%u*t%s ' % (v, k)
            line += '= %d' % b[rowi]
            print(line)
            prints += 1


def print_eqns_np(A_ub, b_ub, verbose=0):
    Adi = A_ub_np2d(A_ub)
    print_eqns(Adi, b_ub, verbose=verbose)


def Ads2bounds(Ads, bs):
    ret = {}
    for row_ds, row_bs in zip(Ads, bs):
        assert len(row_ds) == 1
        k, v = list(row_ds.items())[0]
        assert v == 1
        ret[k] = row_bs
    return ret


def instances(Ads):
    ret = 0
    for row_ds in Ads:
        ret += sum(row_ds.values())
    return ret


def acorner2csv(b, corneri):
    corners = ["None" for _ in range(4)]
    corners[corneri] = str(b)
    return ' '.join(corners)


def corners2csv(bs):
    assert len(bs) == 4
    corners = ["None" if b is None else str(b) for b in bs]
    return ' '.join(corners)


def tilej_stats(tilej):
    stats = {}
    for etype in ('pips', 'wires'):
        tm = stats.setdefault(etype, {})
        tm['net'] = 0
        tm['solved'] = [0, 0, 0, 0]
        tm['covered'] = [0, 0, 0, 0]

    for tile in tilej['tiles'].values():
        for etype in ('pips', 'wires'):
            pips = tile[etype]
            for k, v in pips.items():
                stats[etype]['net'] += 1
                for i in range(4):
                    if pips[k][i]:
                        stats[etype]['solved'][i] += 1
                    if pips[k][i] is not None:
                        stats[etype]['covered'][i] += 1

    for corner, corneri in corner_s2i.items():
        print('Corner %s' % corner)
        for etype in ('pips', 'wires'):
            net = stats[etype]['net']
            solved = stats[etype]['solved'][corneri]
            covered = stats[etype]['covered'][corneri]
            print(
                '  %s: %u / %u solved, %u / %u covered' %
                (etype, solved, net, covered, net))

def load_bounds(bounds_csv, corner, ico=True):
    Ads, b = loadc_Ads_b([bounds_csv], corner, ico=ico)
    return Ads2bounds(Ads, b)
