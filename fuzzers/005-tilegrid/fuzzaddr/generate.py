#!/usr/bin/env python3

from prjxray import bitsmaker


def run(bits_fn, design_fn, fnout, oneval, dframe, dword, dbit, verbose=False):
    metastr = "DFRAME:%02x.DWORD:%u.DBIT:%u" % (dframe, dword, dbit)

    tags = dict()
    f = open(design_fn, 'r')
    f.readline()
    for l in f:
        l = l.strip()
        # Additional values reserved / for debugging
        tile, val = l.split(',')[0:2]
        tags["%s.%s" % (tile, metastr)] = val == oneval

    bitsmaker.write(bits_fn, fnout, tags)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        "Solve bits (like segmaker) on raw .bits file without segments")
    parser.add_argument("--bits-file", default="design.bits", help="")
    parser.add_argument("--verbose", action="store_true", help="")
    parser.add_argument("--design", default="design.csv", help="")
    parser.add_argument("--fnout", default="/dev/stdout", help="")
    parser.add_argument("--oneval", required=True, help="")
    parser.add_argument(
        "--dframe",
        type=str,
        required=True,
        help="Reference frame delta (base 16)")
    parser.add_argument(
        "--dword",
        type=str,
        required=True,
        help="Reference word delta (base 10)")
    parser.add_argument(
        "--dbit",
        type=str,
        required=True,
        help="Reference bit delta (base 10)")
    args = parser.parse_args()

    run(
        args.bits_file,
        args.design,
        args.fnout,
        args.oneval,
        int(args.dframe, 16),
        int(args.dword, 10),
        int(args.dbit, 10),
        verbose=args.verbose)


if __name__ == "__main__":
    main()
