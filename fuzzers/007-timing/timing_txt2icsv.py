#!/usr/bin/env python3

from timfuz import Benchmark, A_di2ds
from timing_txt2json import gen_timing4n, load_speed_json

import glob
import math
import json
import sys
from collections import OrderedDict

# prefix to make easier to track
# models do not overlap between PIPs and WIREs
PREFIX_W = 'WIRE_'
PREFIX_P = 'PIP_'


# Verify the nodes and wires really do line up
def vals2Adi_check(vals, names):
    print('Checking')
    for val in vals:
        node_wires = 0
        for _node, wiresn in val['nodes']:
            node_wires += wiresn
        assert node_wires == len(val['wires'])
    print('Done')
    assert 0


def json2Ads(vals, verbose=False):
    '''Convert timing4 JSON into Ads interconnect equations'''

    def pip2speed(pip):
        _site, _name, pip_name = pip
        return PREFIX_P + pip_name

    def wire2speed(wire):
        _site, _name, wire_name = wire
        return PREFIX_W + wire_name

    print('Making equations')

    def mk_row(val):
        def add_name(name):
            row_ds[name] = row_ds.get(name, 0) + 1

        row_ds = {}

        for pip in val['pips']:
            add_name(pip2speed(pip))
        for wire in val['wires']:
            add_name(wire2speed(wire))
        return row_ds

    return [mk_row(val) for val in vals]


def load_Ads(speed_json_f, fn_ins):

    print('Loading data')

    _speedj, speed_i2s = load_speed_json(speed_json_f)

    for fn_in in fn_ins:
        vals = list(gen_timing4n(fn_in, speed_i2s))
        Ads = json2Ads(vals)

        def mkb(val):
            t = val['t']
            return (t['fast_max'], t['fast_min'], t['slow_max'], t['slow_min'])

        bs = [mkb(val) for val in vals]
        ico = [val['ico'] for val in vals]

        for row_bs, row_ds, row_ico in zip(bs, Ads, ico):
            yield row_bs, row_ds, row_ico


def run(speed_json_f, fout, fns_in, verbose=0, corner=None):
    fout.write('ico,fast_max fast_min slow_max slow_min,rows...\n')
    for row_bs, row_ds, row_ico in load_Ads(speed_json_f, fns_in):
        # XXX: consider removing ico column
        # its obsolete at this point
        if not row_ico:
            continue
        # like: 123 456 120 450, 1 a, 2 b
        # first column has delay corners, followed by delay element count
        items = [str(row_ico), ' '.join([str(x) for x in row_bs])]
        for k, v in sorted(row_ds.items()):
            items.append('%u %s' % (v, k))
        fout.write(','.join(items) + '\n')


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Convert obscure timing4.txt into more readable but roughly equivilent timing4i.csv (interconnect)'
    )

    parser.add_argument('--verbose', type=int, help='')
    # made a bulk conversion easier...keep?
    parser.add_argument(
        '--auto-name', action='store_true', help='timing4.txt => timing4i.csv')
    parser.add_argument(
        '--speed-json',
        default='build_speed/speed.json',
        help='Provides speed index to name translation')
    parser.add_argument('--out', default=None, help='Output timing4i.csv file')
    parser.add_argument('fns_in', nargs='+', help='Input timing4.txt files')
    args = parser.parse_args()
    bench = Benchmark()

    fnout = args.out
    if fnout is None:
        if args.auto_name:
            assert len(args.fns_in) == 1
            fnin = args.fns_in[0]
            fnout = fnin.replace('.txt', 'i.csv')
            assert fnout != fnin, 'Expect .txt in'
        else:
            # practically there are too many stray prints to make this work as expected
            assert 0, 'File name required'
            fnout = '/dev/stdout'
    print("Writing to %s" % fnout)
    fout = open(fnout, 'w')

    fns_in = args.fns_in
    if not fns_in:
        fns_in = glob.glob('specimen_*/timing4.txt')

    run(
        speed_json_f=open(args.speed_json, 'r'),
        fout=fout,
        fns_in=fns_in,
        verbose=args.verbose)


if __name__ == '__main__':
    main()
