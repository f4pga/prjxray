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
'''
This script allows to load a number of .db or .rdb files and display bits in
a nice visualization.

When more than one files are loaded, a difference between them is shown.
Differring bits are highlighted.
'''
import argparse
import re
import sys

import itertools

from prjxray.util import OpenSafeFile

# =============================================================================


def tagmap(tag):
    """
    Maps a specific tag name to its generic name
    """

    tag = tag.replace("CLBLL_L", "CLB")
    tag = tag.replace("CLBLL_M", "CLB")
    tag = tag.replace("CLBLM_L", "CLB")
    tag = tag.replace("CLBLM_M", "CLB")

    tag = tag.replace("SLICEL", "SLICE")
    tag = tag.replace("SLICEM", "SLICE")

    tag = tag.replace("LIOB33", "IOB33")
    tag = tag.replace("RIOB33", "IOB33")

    tag = tag.replace("LIOI3", "IOI3")
    tag = tag.replace("RIOI3", "IOI3")

    # TODO: Add other tag mappings

    return tag


def parse_bit(bit):
    """
    Decodes string describing a bit. Returns a tuple (frame, bit, value)
    """
    match = re.match("^(!?)([0-9]+)_([0-9]+)$", bit)
    assert match != None, bit

    val = int(match.group(1) != "!")
    frm = int(match.group(2))
    bit = int(match.group(3))

    return frm, bit, val


def load_and_sort_segbits(file_name, tagmap=lambda tag: tag):
    """
    Loads a segbit file (.db or .rdb). Skips bits containing '<' or '>'
    """

    # Load segbits
    segbits = {}
    with OpenSafeFile(file_name, "r") as fp:
        lines = fp.readlines()

        # Parse lines
        for line in lines:
            line = line.strip()
            fields = line.split()

            if len(fields) < 2:
                print("Malformed line: '%s'" % line)
                continue

            # Map name
            feature = tagmap(fields[0])

            # Decode bits
            bits = []
            for bit in fields[1:]:
                if "<" in bit or ">" in bit:
                    continue
                bits.append(parse_bit(bit))

            # Sort bits
            bits.sort(key=lambda bit: (bit[0], bit[1],))
            segbits[feature] = bits

    return segbits


# =============================================================================


def make_header_lines(all_bits):
    """
    Formats header lines
    """
    lines = []

    # Bit names
    bit_names = ["%d_%d" % (b[0], b[1]) for b in all_bits]
    bit_len = 6
    for i in range(bit_len):
        line = ""
        for j in range(len(all_bits)):
            bstr = bit_names[j].ljust(bit_len).replace("_", "|")
            line += bstr[i]
        lines.append(line)

    return lines


def make_data_lines(all_tags, all_bits, segbits):
    """
    Formats data lines
    """
    lines = []

    def map_f(b):
        if b < 0: return "0"
        if b > 0: return "1"
        return "-"

    # Bit data
    for tag in all_tags:
        if tag in segbits.keys():
            lines.append("".join(map(map_f, segbits[tag])))
        else:
            lines.append(" " * len(all_bits))

    return lines


def main():

    # Colors for TTY
    if sys.stdout.isatty():
        colors = {
            "NONE": "\033[0m",
            "DIFF": "\033[1m",
        }

    # Colors for pipe
    else:
        colors = {
            "NONE": "",
            "DIFF": "",
        }

    # ........................................................................

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("files", nargs="*", type=str, help="Input files")

    args = parser.parse_args()

    # Load segbits
    all_segbits = []
    for f in args.files:
        all_segbits.append(load_and_sort_segbits(f, tagmap))

    # List of all features and all bits
    all_tags = set()
    all_bits = set()

    for segbits in all_segbits:
        all_tags |= set(segbits.keys())
        for bits in segbits.values():
            all_bits |= set([(b[0], b[1]) for b in bits])

    all_tags = sorted(list(all_tags))
    all_bits = sorted(list(all_bits))

    # Convert bit lists to bit vectors
    for segbits in all_segbits:
        for tag in segbits.keys():
            vec = list([0] * len(all_bits))
            for i, bit in enumerate(all_bits):
                if (bit[0], bit[1], 0) in segbits[tag]:
                    vec[i] = -1
                if (bit[0], bit[1], 1) in segbits[tag]:
                    vec[i] = +1
            segbits[tag] = vec

    # Make header and data lines
    header_lines = make_header_lines(all_bits)
    data_lines = [
        make_data_lines(all_tags, all_bits, segbits) for segbits in all_segbits
    ]

    # Display
    max_tag_len = max([len(tag) for tag in all_tags])

    for l in header_lines:
        line = " " * max_tag_len + " "
        for i in range(len(all_segbits)):
            line += l + " "
        print(line)

    data_len = len(all_bits)
    for i, tag in enumerate(all_tags):
        line = tag.ljust(max_tag_len) + " "

        diff = bytearray(data_len)
        for l1, l2 in itertools.combinations(data_lines, 2):
            for j in range(data_len):
                if l1[i][j] != l2[i][j]:
                    diff[j] = 1

        for l in data_lines:
            for j in range(data_len):
                if diff[j]:
                    line += colors["DIFF"] + l[i][j] + colors["NONE"]
                else:
                    line += l[i][j]
            line += " "

        print(line)


# =============================================================================

if __name__ == "__main__":
    main()
