import json
import csv
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description=
        "Creates design.json from output of ROI generation tcl script.")
    parser.add_argument('--design_txt', required=True)
    parser.add_argument('--design_info_txt', required=True)

    args = parser.parse_args()

    j = {}
    j['ports'] = []
    j['info'] = {}
    with open(args.design_txt) as f:
        for d in csv.DictReader(f, delimiter=' '):
            j['ports'].append(d)

    with open(args.design_info_txt) as f:
        for l in f:
            name, value = l.strip().split(' = ')

            j['info'][name] = int(value)

    json.dump(j, sys.stdout, indent=2, sort_keys=True)


if __name__ == '__main__':
    main()
