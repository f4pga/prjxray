#!/usr/bin/env python3

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

            if speed_model not in timings:
                timings['cells'][speed_model] = dict()

            if site not in timings['cells'][speed_model]:
                timings['cells'][speed_model][site] = dict()

            if speed_model not in timings['cells'][speed_model][site]:
                timings['cells'][speed_model][site][speed_model] = dict()

            delays = dict()
            # each timing entry reports 5 delays
            for d in range(0, 5):
                (t, v) = raw_data[d + 1].split(':')
                delays[t] = v

            # create entry for sdf writer
            port = dict()
            port['port'] = speed_model
            port['edge'] = None
            paths = dict()
            paths = add_timing_paths_entry(
                paths, 'slow', [delays['SLOW_MIN'], None, delays['SLOW_MAX']])
            paths = add_timing_paths_entry(
                paths, 'fast', [delays['FAST_MIN'], None, delays['FAST_MAX']])
            timings['cells'][speed_model][site][
                speed_model] = utils.add_device(port, paths)
            timings['cells'][speed_model][site][speed_model][
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
