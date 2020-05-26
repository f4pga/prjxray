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

import os, sys
from prjxray import util


def run(fn_ins, fn_out, strict=False, track_origin=False, verbose=False):
    # tag to bits
    entries = {}
    # tag to (bits, line)
    tags = dict()
    # bits to (tag, line)
    bitss = dict()

    for fn_in in fn_ins:
        for line, (tag, bits, mode, origin) in util.parse_db_lines(fn_in):
            line = line.strip()
            assert mode is not None or mode != "always", "strict: got ill defined line: %s" % (
                line, )

            if tag in tags:
                orig_bits, orig_line, orig_origin = tags[tag]
                if orig_bits != bits:
                    print(
                        "WARNING: got duplicate tag %s" % (tag, ),
                        file=sys.stderr)
                    print("  Orig line: %s" % orig_line, file=sys.stderr)
                    print("  New line : %s" % line, file=sys.stderr)
                    assert not strict, "strict: got duplicate tag"
                origin = os.path.basename(os.getcwd())
                if track_origin and orig_origin != origin:
                    origin = orig_origin + "," + origin
            if bits in bitss:
                orig_tag, orig_line = bitss[bits]
                if orig_tag != tag:
                    print(
                        "WARNING: got duplicate bits %s" % (bits, ),
                        file=sys.stderr)
                    print("  Orig line: %s" % orig_line, file=sys.stderr)
                    print("  New line : %s" % line, file=sys.stderr)
                    assert not strict, "strict: got duplicate bits"

            if track_origin and origin is None:
                origin = os.path.basename(os.getcwd())
            entries[tag] = (bits, origin)
            tags[tag] = (bits, line, origin)
            if bits != None:
                bitss[bits] = (tag, line)

    util.write_db_lines(fn_out, entries, track_origin)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Combine multiple .db files")

    util.db_root_arg(parser)
    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--track_origin', action='store_true', help='')
    parser.add_argument('--out', help='')
    parser.add_argument('ins', nargs='+', help='Last takes precedence')
    args = parser.parse_args()

    run(
        args.ins,
        args.out,
        strict=int(os.getenv("MERGEDB_STRICT", "1")),
        track_origin=args.track_origin,
        verbose=args.verbose)


if __name__ == '__main__':
    main()
