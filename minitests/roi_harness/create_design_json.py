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
import xjson
import csv
import argparse
import sys
import fasm
from prjxray.db import Database
from prjxray.roi import Roi
from prjxray.util import get_db_root, get_part
from prjxray.xjson import extract_numbers


def set_port_wires(ports, name, pin, wires_outside_roi):
    for port in ports:
        if name == port['name']:
            port['wires_outside_roi'] = sorted(
                wires_outside_roi, key=extract_numbers)
            assert port['pin'] == pin
            return

    assert False, name


def main():
    parser = argparse.ArgumentParser(
        description=
        "Creates design.json from output of ROI generation tcl script.")
    parser.add_argument('--design_txt', required=True)
    parser.add_argument('--design_info_txt', required=True)
    parser.add_argument('--pad_wires', required=True)
    parser.add_argument('--design_fasm', required=True)

    args = parser.parse_args()

    design_json = {}
    design_json['ports'] = []
    design_json['info'] = {}
    with open(args.design_txt) as f:
        for d in csv.DictReader(f, delimiter=' '):
            if d['name'].startswith('dout['):
                d['type'] = 'out'
            elif d['name'].startswith('din['):
                d['type'] = 'in'
            elif d['name'].startswith('clk'):
                d['type'] = 'clk'
            else:
                assert False, d

            design_json['ports'].append(d)

    with open(args.design_info_txt) as f:
        for l in f:
            name, value = l.strip().split(' = ')

            design_json['info'][name] = int(value)

    db = Database(get_db_root(), get_part())
    grid = db.grid()

    roi = Roi(
        db=db,
        x1=design_json['info']['GRID_X_MIN'],
        y1=design_json['info']['GRID_Y_MIN'],
        x2=design_json['info']['GRID_X_MAX'],
        y2=design_json['info']['GRID_Y_MAX'],
    )

    with open(args.pad_wires) as f:
        for l in f:
            parts = l.strip().split(' ')
            name = parts[0]
            pin = parts[1]
            wires = parts[2:]

            wires_outside_roi = []

            for wire in wires:
                tile = wire.split('/')[0]

                loc = grid.loc_of_tilename(tile)

                if not roi.tile_in_roi(loc):
                    wires_outside_roi.append(wire)

            set_port_wires(design_json['ports'], name, pin, wires_outside_roi)

    frames_in_use = set()
    for tile in roi.gen_tiles():
        gridinfo = grid.gridinfo_at_tilename(tile)

        for bit in gridinfo.bits.values():
            frames_in_use.add(bit.base_address)

    required_features = []
    for fasm_line in fasm.parse_fasm_filename(args.design_fasm):
        if fasm_line.annotations:
            for annotation in fasm_line.annotations:
                if annotation.name != 'unknown_segment':
                    continue

                unknown_base_address = int(annotation.value, 0)

                assert False, "Found unknown bit in base address 0x{:08x}".format(
                    unknown_base_address)

        if not fasm_line.set_feature:
            continue

        tile = fasm_line.set_feature.feature.split('.')[0]

        loc = grid.loc_of_tilename(tile)
        gridinfo = grid.gridinfo_at_tilename(tile)

        not_in_roi = not roi.tile_in_roi(loc)

        if not_in_roi:
            required_features.append(fasm_line)

    design_json['required_features'] = sorted(
        fasm.fasm_tuple_to_string(required_features,
                                  canonical=True).split('\n'),
        key=extract_numbers)

    design_json['ports'].sort(key=lambda x: extract_numbers(x['name']))

    xjson.pprint(sys.stdout, design_json)


if __name__ == '__main__':
    main()
