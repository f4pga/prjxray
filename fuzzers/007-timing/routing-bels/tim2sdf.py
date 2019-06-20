#!/usr/bin/env python3

import argparse
import json


def read_raw_timings(fin):

    timings = dict()
    with open(fin, "r") as f:
        for line in f:

            raw_data = line.split()
            speed_model = raw_data[0]

            if speed_model.startswith('bel_d_'):
                speed_model = speed_model[6:]

            if speed_model not in timings:
                timings[speed_model] = dict()

            # each timing entry reports 5 delays
            for d in range(0, 5):
                (t, v) = raw_data[d + 1].split(':')
                timings[speed_model][t] = v

    return timings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--timings', type=str, help='Raw timing input file')
    parser.add_argument('--json', type=str, help='json output file')
    parser.add_argument(
        '--debug', type=bool, default=False, help='Enable debug json dumps')
    args = parser.parse_args()

    timings = read_raw_timings(args.timings)
    with open(args.json, 'w') as fp:
        json.dump(timings, fp, indent=4, sort_keys=True)


if __name__ == '__main__':
    main()
