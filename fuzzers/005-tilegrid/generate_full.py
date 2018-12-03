#!/usr/bin/env python3
import os, sys, json, re


def run(json_in_fn, json_out_fn, deltas_fns, verbose=False):
    database = json.load(open(json_in_fn, "r"))

    # TODO: move address processing here

    # Save
    json.dump(
        database,
        open(json_out_fn, "w"),
        sort_keys=True,
        indent=4,
        separators=(",", ": "))


def main():
    import argparse
    import glob

    parser = argparse.ArgumentParser(
        description="Generate tilegrid.json from bitstream deltas")

    parser.add_argument("--verbose", action="store_true", help="")
    parser.add_argument(
        "--json-in",
        default="tiles_basic.json",
        help="Input .json without addresses")
    parser.add_argument(
        "--json-out", default="tilegrid.json", help="Output JSON")
    parser.add_argument(
        "deltas", nargs="*", help=".bit diffs to create base addresses from")
    args = parser.parse_args()

    deltas = args.deltas
    if not args.deltas:
        deltas = glob.glob("*.delta")

    run(args.json_in, args.json_out, deltas, verbose=args.verbose)


if __name__ == "__main__":
    main()
