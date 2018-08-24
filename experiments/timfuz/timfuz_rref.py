#!/usr/bin/env python3

'''
Triaging tool to help understand where we need more timing coverage
Finds correlated variables to help make better test cases
'''

from timfuz import Benchmark, Ar_di2np, loadc_Ads_b, index_names, A_ds2np
import numpy as np
import glob
import math
import json
import sympy
from collections import OrderedDict

STRICT = 1

class State(object):
    def __init__(self, Ads, drop_names=[]):
        self.Ads = Ads
        self.names = index_names(self.Ads)

        # known zero delay elements
        self.drop_names = set(drop_names)
        # active names in rows
        # includes sub symbols, excludes symbols that have been substituted out
        self.base_names = set(self.names)
        self.names = set(self.base_names)
        # List of variable substitutions
        # k => dict of v:n entries that it came from
        self.subs = {}
        self.verbose = True

    def print_stats(self):
        print("Stats")
        print("  Substitutions: %u" % len(self.subs))
        if self.subs:
            print("    Largest: %u" % max([len(x) for x in self.subs.values()]))
        print("  Rows: %u" % len(self.Ads))
        print("  Cols (in): %u" % (len(self.base_names) + len(self.drop_names)))
        print("  Cols (preprocessed): %u" % len(self.base_names))
        print("    Drop names: %u" % len(self.drop_names))
        print("  Cols (out): %u" % len(self.names))
        assert len(self.names) >= len(self.subs)

    @staticmethod
    def load(fn_ins):
        Ads, _b = loadc_Ads_b(fn_ins, corner=None, ico=True)
        return State(Ads)

def write_state(state, fout):
    j = {
        'names': dict([(x, None) for x in state.names]),
        'drop_names': list(state.drop_names),
        'base_names': list(state.base_names),
        'subs': dict([(name, values) for name, values in state.subs.items()]),
        'pivots': state.pivots,
    }
    json.dump(j, fout, sort_keys=True, indent=4, separators=(',', ': '))

def Adi2matrix(Adi, cols):
    A_ub2 = [np.zeros(cols) for _i in range(cols)]

    dst_rowi = 0
    for row in Adi:
        rownp = Ar_di2np(row, cols=len(names), sf=1)

        A_ub2[dst_rowi] = np.add(A_ub2[dst_rowi], rownp)
        dst_rowi = (dst_rowi + 1) % len(names)

    return A_ub2

def Anp2matrix(Anp):
    ncols = len(Anp[0])
    A_ub2 = [np.zeros(ncols) for _i in range(ncols)]
    dst_rowi = 0
    for rownp in Anp:
        A_ub2[dst_rowi] = np.add(A_ub2[dst_rowi], rownp)
        dst_rowi = (dst_rowi + 1) % ncols
    return A_ub2

def row_np2ds(rownp, names):
    ret = {}
    assert len(rownp) == len(names), (len(rownp), len(names))
    for namei, name in enumerate(names):
        v = rownp[namei]
        if v:
            ret[name] = v
    return ret

def comb_corr_sets(state, verbose=False):
    print('Converting rows to integer keys')
    names, Anp = A_ds2np(state.Ads)

    print('np: %u rows x %u cols' % (len(Anp), len(Anp[0])))
    print('Combining rows into matrix')
    mnp = Anp2matrix(Anp)
    print('Matrix: %u rows x %u cols' % (len(mnp), len(mnp[0])))
    print('Converting np to sympy matrix')
    msym = sympy.Matrix(mnp)
    print('Making rref')
    rref, pivots = msym.rref()

    if verbose:
        print('names')
        print(names)
        print('Matrix')
        sympy.pprint(msym)
        print('Pivots')
        sympy.pprint(pivots)
        print('rref')
        sympy.pprint(rref)

    state.pivots = {}

    def row_solved(rownp, row_pivot):
        for ci, c in enumerate(rownp):
            if ci == row_pivot:
                continue
            if c != 0:
                return False
        return True

    rrefnp = np.array(rref).astype(np.float64)
    print('Computing groups w/ rref %u row x %u col' % (len(rrefnp), len(rrefnp[0])))
    #print(rrefnp)
    # rows that have a single 1 are okay
    # anything else requires substitution (unless all 0)
    # pivots may be fewer than the rows
    # remaining rows should be 0s
    for row_i, (row_pivot, rownp) in enumerate(zip(pivots, rrefnp)):
        rowds = row_np2ds(rownp, names)
        # boring cases: solved variable, not fully ranked
        #if sum(rowds.values()) == 1:
        if row_solved(rownp, row_pivot):
            continue

        # a grouping
        group_name = "GROUP_%u" % row_i
        if STRICT:
            delta = 0.001
            rowds_store = {}
            for k, v in rowds.items():
                vi = int(round(v))
                error = abs(vi - v)
                assert error < delta, (error, delta)
                rowds_store[k] = vi
        else:
            rowds_store = rowds
        state.subs[group_name] = rowds_store
        # Add the new symbol
        state.names.add(group_name)
        # Remove substituted symbols
        # Note: symbols may appear multiple times
        state.names.difference_update(set(rowds.keys()))
        pivot_name = names[row_pivot]
        state.pivots[group_name] = pivot_name
        if verbose:
            print("%s (%s): %s" % (group_name, pivot_name, rowds))

    return state

def run(fout, fn_ins, verbose=0):
    print('Loading data')

    state = State.load(fn_ins)
    comb_corr_sets(state, verbose=verbose)
    state.print_stats()
    if fout:
        write_state(state, fout)

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Timing fuzzer'
    )

    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--speed-json', default='build_speed/speed.json',
        help='Provides speed index to name translation')
    parser.add_argument('--out', help='Output sub.json substitution result')
    parser.add_argument(
        'fns_in',
        nargs='*',
        help='timing3.txt input files')
    args = parser.parse_args()
    bench = Benchmark()

    fout = None
    if args.out:
        fout = open(args.out, 'w')

    fns_in = args.fns_in
    if not fns_in:
        fns_in = glob.glob('specimen_*/timing3.csv')

    try:
        run(fout=fout,
            fn_ins=args.fns_in, verbose=args.verbose)
    finally:
        print('Exiting after %s' % bench)

if __name__ == '__main__':
    main()
