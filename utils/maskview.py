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
"""
This tool allows to view segbits using a 2D frame vs. bit plot. It can read
either mask.db files or segbits.db files. Multiple files can be read at once
allowing to identify where a bit comes from.

When a single file is read, a bit is marked as "O". When multiple files are
read, a bit is denoted with a letter "A", "B" and so on depending on index
of file that it belongs to.

Duplicate bits (present in more than one files) are marked with "#"
"""

import sys
import argparse
import re

from prjxray.util import OpenSafeFile

# =============================================================================


def load_just_bits(file_name):
    """
    Read bits from a .db or .rdb file. Ignores tags and bit values.
    """

    with OpenSafeFile(file_name, "r") as fp:
        lines = fp.readlines()

    bits = set()
    for line in lines:
        for word in line.split(" "):
            match = re.match("^(!?)([0-9]+)_([0-9]+)$", word)
            if match is not None:
                frm = int(match.group(2))
                bit = int(match.group(3))

                bits.add((
                    frm,
                    bit,
                ))

    return bits


# =============================================================================


def main():

    # Colors for TTY
    if sys.stdout.isatty():

        bit_colors = [
            "\033[39m",
            "\033[91m",
            "\033[92m",
            "\033[93m",
            "\033[94m",
            "\033[95m",
            "\033[96m",
            "\033[31m",
            "\033[32m",
            "\033[33m",
            "\033[34m",
            "\033[35m",
            "\033[36m",
        ]

        colors = {
            "NONE": "\033[0m",
            "DUPLICATE": "\033[101;97m",
        }

    # Colors for pipe
    else:

        bit_colors = [""]

        colors = {
            "NONE": "",
            "DUPLICATE": "",
        }

    # .........................................................................

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("files", nargs="*", type=str, help="Input files")

    args = parser.parse_args()

    # Load bits
    all_bits = []
    for i, f in enumerate(args.files):
        bits = load_just_bits(f)
        all_bits.append(bits)

        cstr = bit_colors[i % len(bit_colors)]
        bstr = "O" if len(args.files) == 1 else chr(65 + i)
        print(cstr + bstr + colors["NONE"] + ": %s #%d" % (f, len(bits)))

    print("")

    max_frames = max([bit[0] for bits in all_bits for bit in bits]) + 1
    max_bits = max([bit[1] for bits in all_bits for bit in bits]) + 1

    # Header
    for r in range(3):
        line = " " * 3
        for c in range(max_bits):
            bstr = "%03d" % c
            line += bstr[r]
        print(line)

    print("")

    # Display bits
    for r in range(max_frames):
        line = "%2d " % r
        for c in range(max_bits):
            got_bit = False
            bit_str = colors["NONE"] + "-"
            for i, bits in enumerate(all_bits):
                cstr = bit_colors[i % len(bit_colors)]
                bstr = "O" if len(args.files) == 1 else chr(65 + i)
                if (r, c) in bits:
                    if not got_bit:
                        bit_str = cstr + bstr
                    else:
                        bit_str = colors["DUPLICATE"] + "#" + colors["NONE"]
                    got_bit = True

            line += bit_str

        line += colors["NONE"]
        print(line)


# =============================================================================

if __name__ == "__main__":
    main()
