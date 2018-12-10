#!/usr/bin/env python3

import sys, re
from prjxray import util


def run(fnin, fnout=None, strict=False, verbose=False):
    lines = open(fnin, 'r').read().split('\n')
    tags = dict()
    bitss = set()
    for line in lines:
        line = line.strip()
        if line == '':
            continue
        # TODO: figure out what to do with masks
        if line.startswith("bit "):
            continue
        tag, bits, mode = util.parse_db_line(line)
        if strict:
            if mode != "always":
                assert not mode, "strict: got ill defined line: %s" % (line, )
            if tag in tags:
                print("Original line: %s" % tags[tag])
                print("New line: %s" % line)
                assert 0, "strict: got duplicate tag %s" % (tag, )
            assert bits not in bitss, "strict: got duplicate bits %s (ex: %s)" % (
                bits, line)
        tags[tag] = line
        if bits != None:
            bitss.add(bits)

    if fnout:
        with open(fnout, "w") as fout:
            for line in sorted(lines):
                line = line.strip()
                if line == '':
                    continue
                fout.write(line + '\n')


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Parse a db, check for consistency")

    util.db_root_arg(parser)
    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Complain on unresolved entries (ex: <0 candidates>, <const0>)')
    parser.add_argument('fin', help='')
    parser.add_argument('fout', nargs='?', help='')
    args = parser.parse_args()

    run(args.fin, args.fout, strict=args.strict, verbose=args.verbose)


if __name__ == '__main__':
    main()
