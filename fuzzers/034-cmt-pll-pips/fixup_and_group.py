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
This is a db fixup script that does two things:

1. Clears (removes) all bits found in "IN_USE" tag(s) and removes the IN_USE
   tag itself

2. Reads tag group definition from a file and applies the tag grouping. First
   a set of common bits for each group is found (logical OR among all tags
   belonging to the group). Then in each tag belonging to the group those
   bits are set to 0 but only if they are not already present there.

The resulting data is written into a segbits file.
"""
import argparse
import re
import itertools

# =============================================================================


def load_tag_groups(file_name):
    """
    Loads tag groups from a text file.

    A tag group is defined by specifying a space separated list of tags within
    a single line. Lines that are empty or start with '#' are ignored.
    """
    tag_groups = []

    # Load tag group specifications
    with open(file_name, "r") as fp:
        for line in fp:
            line = line.strip()

            if len(line) == 0 or line.startswith("#"):
                continue

            group = set(line.split())
            if len(group):
                tag_groups.append(group)

    # Check if all tag groups are exclusive
    for tag_group_a, tag_group_b in itertools.combinations(tag_groups, 2):

        tags = tag_group_a & tag_group_b
        if len(tags):
            raise RuntimeError(
                "Tag(s) {} are present in multiple groups".format(
                    " ".join(tags)))

    return tag_groups


# =============================================================================


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


def bit_to_str(bit):
    """
    Converts a tuple (frame, bit, value) to its string representation.
    """
    s = "!" if not bit[2] else ""
    return "{}{}_{:02d}".format(s, bit[0], bit[1])


def load_segbits(file_name):
    """
    Loads a segbits file.
    """

    segbits = {}

    with open(file_name, "r") as fp:
        for line in fp:
            line = line.strip()
            fields = line.split()

            if len(fields) < 2:
                raise RuntimeError("Malformed line: '%s'" % line)

            tag = fields[0]

            if "<" in line or ">" in line:
                segbits[tag] = set()

            else:
                bits = set([parse_bit(bit) for bit in fields[1:]])
                segbits[tag] = bits

    return segbits


def save_segbits(file_name, segbits):
    """
    Save segbits to a .db or .rdb file
    """

    with open(file_name, "w") as fp:
        for tag, bits in segbits.items():
            if not len(bits):
                continue

            line = tag + " "
            line += " ".join([bit_to_str(bit) for bit in sorted(list(bits))])
            fp.write(line + "\n")


# =============================================================================


def mask_out_bits(segbits, mask, tags_to_mask=None):
    """
    Given a set of bits and a list of tags to affect (optional) removes all
    the bits from each tag that are present (and equal) in the masking set.
    """

    if tags_to_mask is None:
        tags_to_mask = segbits.keys()

    # Mask out matching bits
    for tag in tags_to_mask:
        bits = segbits[tag]

        bits = set(bits) - set(mask)
        segbits[tag] = bits

    return segbits


def find_common_bits_for_tag_groups(segbits, tag_groups):
    """
    For each tag group finds a common set of bits that have value of one.
    """

    bit_groups = []

    for tag_group in tag_groups:
        bit_group = set()

        for tag, bits in segbits.items():
            if tag in tag_group:
                ones = set([b for b in bits if b[2]])
                bit_group |= ones

        bit_groups.append(bit_group)

    return bit_groups


def group_tags(segbits, tag_groups, bit_groups):
    """
    Implements tag grouping. If a tag belongs to a group then the common bits
    of that group are added to is as zeros.
    """

    for tag_group, bit_group in zip(tag_groups, bit_groups):
        zeros = set([(b[0], b[1], 0) for b in bit_group])
        for tag in tag_group:

            # Insert zero bits
            if tag in segbits.keys():
                bits = segbits[tag]
                for z in zeros:
                    if not (z[0], z[1], 1) in bits:
                        bits.add(z)

    return segbits


# =============================================================================


def main():

    # Parse arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", required=True, type=str, help="Input .rdb file")
    parser.add_argument(
        "-g", required=True, type=str, help="Input tag group definition file")
    parser.add_argument("-o", required=True, type=str, help="Output .rdb file")

    args = parser.parse_args()

    # Load tag groups
    tag_groups = load_tag_groups(args.g)

    # Load raw database file
    segbits = load_segbits(args.i)

    # Mask out bits present in "IN_USE" tag(s) as they are common to other tags
    for tag in segbits.keys():
        if tag.endswith("IN_USE"):
            prefix = tag[:tag.index("IN_USE")]
            tags_to_mask = [t for t in segbits.keys() if t.startswith(prefix)]
            mask_out_bits(segbits, segbits[tag], tags_to_mask)

    tags_to_remove = set()
    for tag, bits in segbits.items():
        if len(bits) == 0:
            tags_to_remove.add(tag)

    for tag in tags_to_remove:
        del segbits[tag]

    for tag in segbits.keys():
        if tag.endswith("_ACTIVE") and 'FREQ_BB' in tag:
            m = re.search('FREQ_BB([0-9])', tag)
            l_prefix = '.CMT_TOP_L_UPPER_T_FREQ_BB{}'.format(m.group(1))
            r_prefix = '.CMT_TOP_R_UPPER_T_FREQ_BB{}'.format(m.group(1))

            l_tags_to_mask = [t for t in segbits.keys() if t.endswith(l_prefix)]
            r_tags_to_mask = [t for t in segbits.keys() if t.endswith(r_prefix)]

            mask_out_bits(segbits, segbits[tag], l_tags_to_mask)
            mask_out_bits(segbits, segbits[tag], r_tags_to_mask)

    # Find common bits
    bit_groups = find_common_bits_for_tag_groups(segbits, tag_groups)
    # Apply tag grouping
    segbits = group_tags(segbits, tag_groups, bit_groups)

    # Save fixed database file
    save_segbits(args.o, segbits)


if __name__ == "__main__":
    main()
