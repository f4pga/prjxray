#!/usr/bin/env python3

import argparse
import json

import sdflex
import sdfyacc

sdfyacc.timings = dict()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sdf', type=str, help='Path to input SDF file')
    parser.add_argument('--json', type=str, help='Path to output JSON')

    args = parser.parse_args()

    timings = dict()

    with open(args.sdf, 'r') as fp:

        sdfyacc.parser.parse(fp.read())

    with open(args.json, 'w') as fp:
        json.dump(sdfyacc.timings, fp, indent=4, sort_keys=True)


if __name__ == '__main__':
    main()
