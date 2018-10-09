#!/usr/bin/env python3

import timfuz
from timfuz import loadc_Ads_bs, Ads2bounds, PREFIX_W, PREFIX_P, PREFIX_SW_EI, PREFIX_SW_EO, PREFIX_SW_I, sw_ei_s2vals, sw_eo_s2vals, sw_i_s2vals

import sys
import os
import time
import json


def add_pip_wire(tilej, bounds, verbose=False):
    '''
    We know all possible pips and wires from tilej
    Iterate over them and see if a result was generated
    '''
    used_bounds = set()

    for tile in tilej['tiles'].values():

        def addk(pws, prefix, k, v):
            variable = prefix + ':' + v
            val = bounds.get(variable, None)
            # print(variable, val)
            if val:
                used_bounds.add(variable)
            else:
                val = [None, None, None, None]
            pws[k] = val

        pips = tile['pips']
        for k, v in pips.items():
            #pips[k] = bounds.get('PIP_' + v, [None, None, None, None])
            addk(pips, PREFIX_P, k, v)

        wires = tile['wires']
        for k, v in wires.items():
            #wires[k] = bounds.get('WIRE_' + v, [None, None, None, None])
            addk(wires, PREFIX_W, k, v)

    # verify all the variables that should be used were applied
    # ...except tilecon may be an ROI and we solved everything
    print(
        "Interconnect: %u / %u variables used" %
        (len(used_bounds), len(bounds)))
    if verbose:
        print('Remainder: %s' % (set(bounds.keys()) - used_bounds))


def add_sites(tilej, bounds):
    # XXX: no source of truth currently
    # is there a way we could get this?
    # Naming discussion https://github.com/SymbiFlow/prjxray/pull/126

    sitej = tilej.setdefault('sites', {})

    def add_ei():
        for variable, bound in bounds[PREFIX_SW_EI].items():
            site_type, src_site_pin, dst_bel_type, dst_bel_pin = sw_ei_s2vals(
                variable)
            # ex: SLICEL:AX->AFF.D
            k = (
                '%s:%s->%s.%s' %
                (site_type, src_site_pin, dst_bel_type, dst_bel_pin))
            sitej.setdefault(site_type, {})[k] = bound

    def add_eo():
        for variable, bound in bounds[PREFIX_SW_EO].items():
            site_type, src_bel_type, src_bel_pin, dst_site_pin = sw_eo_s2vals(
                variable)
            # ex: SLICEL:AFF.Q->AQ
            k = (
                '%s:%s.%s->%s' %
                (site_type, src_bel_type, src_bel_pin, dst_site_pin))
            sitej.setdefault(site_type, {})[k] = bound

    def add_i():
        for variable, bound in bounds[PREFIX_SW_I].items():
            site_type, src_bel, src_bel_pin, dst_bel, dst_bel_pin = sw_i_s2vals(
                variable)
            # ex: SLICEL:LUT6.O2->AFF.D
            k = (
                '%s:%s.%s->%s.%s' %
                (site_type, src_bel, src_bel_pin, dst_bel, dst_bel_pin))
            sitej.setdefault(site_type, {})[k] = bound

    add_ei()
    add_eo()
    add_i()
    print('Sites: added %u sites' % len(sitej))
    print('Added site wires')
    print('  Site external in: %u' % len(bounds[PREFIX_SW_EI]))
    print('  Site external out: %u' % len(bounds[PREFIX_SW_EO]))
    print('  Site internal: %u' % len(bounds[PREFIX_SW_I]))


def sep_bounds(bounds):
    pw = {}
    sites = {PREFIX_SW_EI: {}, PREFIX_SW_EO: {}, PREFIX_SW_I: {}}
    for k, v in bounds.items():
        prefix = k.split(':')[0]
        if prefix in (PREFIX_W, PREFIX_P):
            pw[k] = v
        elif prefix in (PREFIX_SW_EI, PREFIX_SW_EO, PREFIX_SW_I):
            sites[prefix][k] = v
        else:
            assert 0, 'Unknown delay: %s %s' % (k, prefix)
    return pw, sites


def run(fns_in, fnout, tile_json_fn, verbose=False):
    # modified in place
    tilej = json.load(open(tile_json_fn, 'r'))

    for fnin in fns_in:
        Ads, bs = loadc_Ads_bs([fnin])
        bounds = Ads2bounds(Ads, bs)
        bounds_pw, bounds_sites = sep_bounds(bounds)
        print(len(bounds), len(bounds_pw), len(bounds_sites))

        add_pip_wire(tilej, bounds_pw)
        add_sites(tilej, bounds_sites)

    timfuz.tilej_stats(tilej)

    json.dump(
        tilej,
        open(fnout, 'w'),
        sort_keys=True,
        indent=4,
        separators=(',', ': '))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Substitute timgrid timing model names for real timing values')
    parser.add_argument(
        '--timgrid-s',
        default='../../timgrid/build/timgrid-s.json',
        help='tilegrid timing delay symbolic input (timgrid-s.json)')
    parser.add_argument(
        '--out',
        default='build/timgrid-vc.json',
        help='tilegrid timing delay values at corner (timgrid-vc.json)')
    parser.add_argument(
        'fn_ins', nargs='+', help='Input flattened timing csv (flat.csv)')
    args = parser.parse_args()

    run(args.fn_ins, args.out, args.timgrid_s, verbose=False)


if __name__ == '__main__':
    main()
