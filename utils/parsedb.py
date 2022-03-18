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

import sys, re
from prjxray.util import OpenSafeFile, db_root_arg, parse_db_line


def run(fnin, fnout=None, strict=False, verbose=False):
    with OpenSafeFile(fnin) as f:
        lines = f.read().split('\n')
    tags = dict()
    bitss = dict()
    for line in lines:
        line = line.strip()
        if line == '':
            continue
        # TODO: figure out what to do with masks
        if line.startswith("bit "):
            continue
        tag, bits, mode, _ = parse_db_line(line)
        if strict:
            if mode != "always":
                assert not mode, "strict: got ill defined line: %s" % (line, )
            if tag in tags:
                print("Original line: %s" % tags[tag], file=sys.stderr)
                print("New line: %s" % line, file=sys.stderr)
                assert 0, "strict: got duplicate tag %s" % (tag, )
            assert bits not in bitss, "strict: got duplicate bits %s: %s %s" % (
                bits, tag, bitss[bits])
        tags[tag] = line
        if bits != None:
            bitss[bits] = tag

    if fnout:
        with OpenSafeFile(fnout, "w") as fout:
            for line in sorted(lines):
                line = line.strip()
                if line == '':
                    continue
                fout.write(line + '\n')


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Parse a db file, checking for consistency")

    db_root_arg(parser)
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
