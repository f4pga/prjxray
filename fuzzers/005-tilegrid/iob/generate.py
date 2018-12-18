#!/usr/bin/env python3

import bitsmaker


def run(bits_fn, design_fn, fnout, verbose=False):
    # Raw: IOB_X0Y101 00020027_003_03
    metastr = "DFRAME:27.DWORD:3.DBIT:3"

    tags = dict()
    f = open(design_fn, 'r')
    f.readline()
    for l in f:
        l = l.strip()
        port, site, tile, pin, val = l.split(',')
        '''
        PULLTYPE    28  29  30
        NONE                X
        KEEPER      X       X
        PULLDOWN
        PULLUP          X   X
        '''
        tags["%s.%s" % (tile, metastr)] = val == "KEEPER"

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
    args = parser.parse_args()

    run(args.bits_file, args.design, args.fnout, args.verbose)


if __name__ == "__main__":
    main()
