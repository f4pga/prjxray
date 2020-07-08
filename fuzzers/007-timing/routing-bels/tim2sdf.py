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

import argparse
import json
from sdf_timing import sdfparse
from sdf_timing import utils


def generate_sdf(timings, sdffile):

    sdf_data = sdfparse.emit(timings, timescale='1ns')
    with open(sdffile, 'w') as fp:
        fp.write(sdf_data)


def add_timing_paths_entry(paths, type, values):
    paths[type] = dict()
    paths[type]['min'] = values[0]
    paths[type]['avg'] = values[1]
    paths[type]['max'] = values[2]
    return paths


def read_raw_timings(fin, site):

    timings = dict()
    timings['cells'] = dict()
    with open(fin, "r") as f:
        for line in f:

            raw_data = line.split()
            speed_model = raw_data[0]

            if speed_model.startswith('bel_d_'):
                speed_model = speed_model[6:]

            speed_model_split = speed_model.split('_')
            interconn_input = "_".join(speed_model_split[1:-1])
            interconn_output = speed_model_split[-1]
            celltype = "ROUTING_BEL"

            if celltype not in timings['cells']:
                timings['cells'][celltype] = dict()

            cellsite = site + '/' + interconn_output.upper()

            if cellsite not in timings['cells'][celltype]:
                timings['cells'][celltype][cellsite] = dict()

            if speed_model not in timings['cells'][celltype][cellsite]:
                timings['cells'][celltype][cellsite][speed_model] = dict()

            delays = dict()
            # each timing entry reports 5 delays
            for d in range(0, 5):
                (t, v) = raw_data[d + 1].split(':')
                delays[t] = v

            # create entry for sdf writer
            iport = dict()
            iport['port'] = interconn_input
            iport['port_edge'] = None
            oport = dict()
            oport['port'] = interconn_output
            oport['port_edge'] = None
            paths = dict()
            paths = add_timing_paths_entry(
                paths, 'slow', [delays['SLOW_MIN'], None, delays['SLOW_MAX']])
            paths = add_timing_paths_entry(
                paths, 'fast', [delays['FAST_MIN'], None, delays['FAST_MAX']])

            if speed_model.endswith('diff'):
                iport['port'] = "_".join(speed_model_split[1:])
                iport['port_edge'] = None
                timings['cells'][celltype][cellsite][
                    speed_model] = utils.add_device(iport, paths)
            else:
                timings['cells'][celltype][cellsite][
                    speed_model] = utils.add_interconnect(iport, oport, paths)
            timings['cells'][celltype][cellsite][speed_model][
                'is_absolute'] = True

    return timings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--timings', type=str, help='Raw timing input file')
    parser.add_argument('--sdf', type=str, help='output sdf file')
    parser.add_argument(
        '--site', type=str, help='Site of the processed timings')
    parser.add_argument(
        '--debug', type=bool, default=False, help='Enable debug json dumps')
    args = parser.parse_args()

    timings = read_raw_timings(args.timings, args.site)
    if args.debug:
        with open("debug" + args.site + ".json", 'w') as fp:
            json.dump(timings, fp, indent=4, sort_keys=True)

    generate_sdf(timings, args.sdf)


if __name__ == '__main__':
    main()
