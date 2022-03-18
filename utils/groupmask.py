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

import sys, os, re
from prjxray.util import OpenSafeFile, parse_db_lines, write_db_lines


def index_masks(fn_in, groups_in):
    """Return a dictionary with the bits active in each group for the specified list of groups"""
    # Only analyze the given groups
    groups = {}
    for group in groups_in:
        groups[group] = set()

    # Index bits
    for line, (tag, bits, mode) in parse_db_lines(fn_in):
        assert not mode, "Unresolved tag: %s" % (line, )
        prefix = tag[0:tag.rfind(".")]
        group = groups.get(prefix, None)
        # Drop groups we aren't interested in
        if group is None:
            continue
        for bit in bits:
            bit = bit.replace("!", "")
            group.add(bit)

    # Verify we were able to find all groups
    for groupk, groupv in groups.items():
        assert len(groupv), "Bad group %s" % groupk

    return groups


def apply_masks(fn_in, groups):
    """Add 0 entries ("!") to .db entries based on groups definition"""
    new_db = {}
    for line, (tag, bits, mode) in parse_db_lines(fn_in):
        assert not mode, "Unresolved tag: %s" % (line, )
        prefix = tag[0:tag.rfind(".")]
        group = groups.get(prefix, None)
        if group:
            bits = set(bits)
            for bit in group:
                if bit not in bits:
                    bits.add("!" + bit)
            bits = frozenset(bits)
        new_db[tag] = bits
    return new_db


def load_groups(fn):
    ret = []
    with OpenSafeFile(fn, "r") as f:
        for l in f:
            ret.append(l.strip())
    return ret


def run(fn_in, fn_out, groups_fn, verbose=False):
    groups_in = load_groups(groups_fn)
    groups = index_masks(fn_in, groups_in)
    new_db = apply_masks(fn_in, groups)
    write_db_lines(fn_out, new_db)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Create multi-bit entries')
    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument(
        '--groups-fn',
        default="groups.grp",
        help='File containing one group per line to parse')
    parser.add_argument('fn_in', help='')
    parser.add_argument('fn_out', help='')
    args = parser.parse_args()

    run(args.fn_in, args.fn_out, args.groups_fn, verbose=args.verbose)


if __name__ == '__main__':
    main()
