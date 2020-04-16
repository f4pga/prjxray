#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

import sys, os, argparse
from sdf_timing import sdfparse

model_carry4 = {
    'type': 'CARRY4',
    'srcs': {'O5', '?X', '?X_LFF', '?X_LBOTH'},
    'out': {'CO0', 'CO1', 'CO2', 'CO3', 'O0', 'O1', 'O2', 'O3'},
    'mux': '?CY0',
    'pins': {
        'DI0': {
            'type': 'A'
        },
        'DI1': {
            'type': 'B'
        },
        'DI2': {
            'type': 'C'
        },
        'DI3': {
            'type': 'D'
        },
    },
}


def compute_delays(model, fin_name, fout_name):
    data = ''
    with open(fin_name, 'r') as f:
        data = f.read()
    sdf = sdfparse.parse(data)

    keys = sdf['cells'][model['type']].keys()
    if 'slicel'.upper() in keys:
        sl = 'L'
    elif 'slicem'.upper() in keys:
        sl = 'M'
    else:
        print("Unknown slice type!")
        return

    nsdf = dict()
    nsdf['header'] = sdf['header']
    nsdf['cells'] = dict()
    nsdf['cells']['ROUTING_BEL'] = dict()

    for p in model['pins']:
        pin = model['pins'][p]

        outs = dict()
        for o in model['out']:
            outs[o] = []

        res = []
        cells = sdf['cells']

        for src in model['srcs']:
            source = src.replace('?', pin['type'])

            _type = model['type'] + '_' + source

            if _type in cells.keys():
                cell = cells[_type]["SLICE" + sl.upper()]

                for o in model['out']:
                    iopath = 'iopath_' + p + '_' + o

                    if iopath in cell.keys():
                        delay = cell[iopath]['delay_paths']['slow']['max']
                        outs[o].append(delay)

        for src in outs:
            s = sorted(outs[src])
            for val in s:
                res.append(val - s[0])

        delay = round(max(res), 3)

        muxname = str(model['mux'].replace('?', pin['type']))
        rbel = nsdf['cells']['ROUTING_BEL']['SLICE' + sl.upper() + '/' +
                                            muxname] = dict()

        iname = 'interconnect_' + pin['type'].lower() + 'x_' + str(p).lower()

        rbel[iname] = dict()
        rbel[iname]['is_absolute'] = True
        rbel[iname]['to_pin_edge'] = None
        rbel[iname]['from_pin_edge'] = None
        rbel[iname]['from_pin'] = pin['type'].lower() + 'x'
        rbel[iname]['to_pin'] = str(p).lower()
        rbel[iname]['type'] = 'interconnect'
        rbel[iname]['is_timing_check'] = False
        rbel[iname]['is_timing_env'] = False

        paths = rbel[iname]['delay_paths'] = dict()

        paths['slow'] = dict()
        paths['slow']['min'] = delay
        paths['slow']['avg'] = None
        paths['slow']['max'] = delay

        paths['fast'] = dict()
        paths['fast']['min'] = delay
        paths['fast']['avg'] = None
        paths['fast']['max'] = delay

        # emit new sdfs
        with open(fout_name, 'w') as f:
            f.write(sdfparse.emit(nsdf))


def main(argv):
    parser = argparse.ArgumentParser(
        description='Tool for computing CARRY4 muxes delays')
    parser.add_argument(
        '--input', dest='inputfile', action='store', help='Input file')
    parser.add_argument(
        '--output', dest='outputfile', action='store', help='Output file')
    args = parser.parse_args(argv[1:])

    compute_delays(model_carry4, args.inputfile, args.outputfile)


if __name__ == "__main__":
    main(sys.argv)
