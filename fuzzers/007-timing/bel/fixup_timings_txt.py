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

import argparse


def fix_line(line, site, filetype):
    """
    Squashes the entries for multiple sites into one.
    This is required when entries are defined for a different
    site than they are reported.
    Such situation happend e.g.
    for BRAM_[LR]. All the entries are defined for RAMBFIFO36E1,
    while they are reported for RAMB18E1 or FIFO18E1

    Parameters
    ----------
    line: str
        raw dump file line
    site: str
        site to which all the entries will be squashed
    filetype: str
        entries type. One of [timings, pins, properties]

    Returns
    -------
    str
        line with squashed entries
    """

    assert filetype in [
        "timings", "pins", "properties"
    ], "Unsupported filetype"

    line = line.split()
    newline = list()
    sites_count = int(line[1])
    newline.append(line[0])
    # we'll emit only one site
    newline.append("1")
    newline.append(site)
    newline.append("1")
    newline.append(site)
    entries = list()
    all_entries = 0
    loc = 2
    for site in range(0, sites_count):
        bels_count = int(line[loc + 1])
        loc += 2
        for bel in range(0, bels_count):
            entries_count = int(line[loc + 1])
            loc += 2
            all_entries += entries_count
            for entry in range(0, entries_count):
                if filetype == 'timings':
                    for delay_word in range(0, 6):
                        entries.append(line[loc])
                        loc += 1
                elif filetype == 'pins':
                    for pin_word in range(0, 4):
                        entries.append(line[loc])
                        loc += 1
                elif filetype == 'properties':
                    entries.append(line[loc])
                    loc += 1
                    values_count = int(line[loc])
                    entries.append(line[loc])
                    loc += 1
                    for value in range(0, values_count):
                        entries.append(line[loc])
                        loc += 1
    newline.append(str(all_entries))
    newline.extend(entries)
    return " ".join(newline) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--txtin', type=str, help='Input text file')
    parser.add_argument('--txtout', type=str, help='Output text file')
    parser.add_argument(
        '--site',
        type=str,
        help='Site to which the entries should be squashed')
    parser.add_argument(
        '--slice', type=str, help='Slice for which the entries shall be fixed')
    parser.add_argument(
        '--type', type=str, choices=['timings', 'pins', 'properties'])

    args = parser.parse_args()
    lines = list()

    with open(args.txtin, 'r') as fp:
        for line in fp:
            if line.startswith(args.slice):
                line = fix_line(line, args.site, args.type)
            lines.append(line)

    with open(args.txtout, 'w') as fp:
        for line in lines:
            fp.write(line)


if __name__ == "__main__":
    main()
