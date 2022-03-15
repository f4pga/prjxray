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

import itertools
import os
import re

from prjxray import util

clb_int_zero_db = [
    # CLB interconnet
    # Ex:
    # segbits_hclk_l.db:73:HCLK_L.HCLK_LEAF_CLK_B_BOTL4.HCLK_CK_BUFHCLK10 00_21 04_21
    # segbits_int_l.db:207:INT_L.CLK_L0.GCLK_L_B8_WEST !01_21 00_21 00_25 01_20 01_24
    "00_21 00_22 00_26 01_28|00_25 01_20 01_21 01_24",
    "00_23 00_30 01_22 01_25|00_27 00_29 01_26 01_29",
    "01_12 01_14 01_16 01_18|00_10 00_11 01_09 01_10",
    "00_13 01_17 00_15 00_17|00_18 00_19 01_13 00_14",
    "00_34 00_38 01_33 01_37|00_35 00_39 01_38 01_40",
    "00_33 00_41 01_32 01_34|00_37 00_42 01_36 01_41",
]


def zero_range(tag, bits, wordmin, wordmax):
    """
    If any bits occur wordmin <= word <= wordmax,
    default bits in wordmin <= word <= wordmax to 0
    """

    # The bit index, if any, that needs to be one hotted
    bitidx = None
    for bit in bits:
        if bit[0] == "!":
            continue
        fidx, bidx = [int(s) for s in bit.split("_")]
        if wordmin <= fidx <= wordmax:
            if bitidx is not None and bidx != bitidx:
                print("Old bit index: %u, new: %u" % (bitidx, bidx))
                print("%s bits: %s" % (tag, str(bits)))
                raise ValueError("%s: inconsistent bit index" % tag)
            bitidx = bidx

    if bitidx is None:
        return

    for fidx in range(wordmin, wordmax + 1):
        bit = "%02d_%02d" % (fidx, bitidx)
        # Preserve 1 bits, set others to 0
        if bit not in bits:
            bits.add("!" + bit)


def bits_str(bits):
    """Convert a set into canonical form"""
    return ' '.join(sorted(list(bits)))


class ZeroGroups(object):
    def __init__(self, zero_db):
        self.groups = []
        self.bit_to_group = {}
        self.tag_to_groups = {}
        self.zero_tag_to_group = {}
        self.parse_zero_db(zero_db)

    def print_groups(self):
        print('Zero groups:')
        for bits in self.groups:
            print(bits_str(bits))

        print('Zero tags:')
        for tag in self.zero_tag_to_group:
            print(tag, bits_str(self.zero_tag_to_group[tag]))

    def parse_zero_db(self, zero_db):
        """ Convert zero db format into data structure

        Zero db format examples:

        Ex: 01_02 04_05
        Means find a line that has either of these bits
        If either of them occurs, default bits in that set to zero

        Ex: 01_02 04_05|07_08 10_11
        If any bits from the first group occur,
        default bits in the second group to zero

        Ex: 01_02 04_05,ALL_ZERO
        ALL_ZERO is an enum that is part of the group but is all 0
        It must have 0 candidates

        Ex: CLB.SLICE_X0.CLKINV ^ CLB.SLICE_X0.NOCLKINV
        CLB.SLICE_X0.NOCLKINV is all bits in CLB.SLICE_X0.CLKINV unset

        Ex: A | B ^ C
        C is all bits in (A)|(B) unset


        """
        for zdb in zero_db:

            if "^" in zdb:
                self.groups.append(set())
                zero_group = self.groups[-1]

                other_tags, allzero_tag = zdb.split('^')
                allzero_tag = allzero_tag.strip()

                for tag in other_tags.split():
                    self.tag_to_groups[tag.strip()] = [zero_group]

                self.zero_tag_to_group[allzero_tag] = zero_group
                continue

            allzero_tag = None
            if "," in zdb:
                zdb, allzero_tag = zdb.split(",")

            if "|" in zdb:
                a, b = zdb.split("|")
                a = a.split()
                b = b.split()

                self.groups.append(set(b))
                zero_group = self.groups[-1]
            else:
                a = zdb.split()
                self.groups.append(set(a))
                zero_group = self.groups[-1]

            if allzero_tag is not None:
                self.zero_tag_to_group[allzero_tag] = zero_group

            for bit in a:
                self.bit_to_group[bit] = zero_group

    def add_tag_bits(self, tag, bits):
        if tag in self.zero_tag_to_group:
            return

        group_ids = set()
        groups = []

        if tag in self.tag_to_groups:
            assert len(self.tag_to_groups[tag]) == 1

            self.tag_to_groups[tag][0] |= bits

            for bit in bits:
                if bit in self.bit_to_group:
                    # Make sure each bit only belongs to one group
                    assert id(self.bit_to_group[bit]) == id(
                        self.tag_to_groups[tag])
                else:
                    self.bit_to_group[bit] = self.tag_to_groups[tag]

            group_ids.add(id(self.tag_to_groups[tag]))
            groups = self.tag_to_groups[tag]

        for bit in bits:
            if bit in self.bit_to_group:
                if id(self.bit_to_group[bit]) not in group_ids:
                    group_ids.add(id(self.bit_to_group[bit]))
                    groups.append(self.bit_to_group[bit])

        self.tag_to_groups[tag] = groups

    def add_bits_from_zero_groups(self, tag, bits, strict=True, verbose=False):
        """ Add bits from a zero group, if needed

        Arguments
        ---------
        tag : str
            Tag being to examine for zero group
        bits : set of str
            Set of bits set on this tag
        strict : bool
            Assert that the size of the given group is the size of the given
            mask.
        verbose : bool
            Print to stdout grouping being made
        """

        tag_is_masked = tag in self.tag_to_groups
        tag_is_zero = tag in self.zero_tag_to_group

        # Should not have a tag that is both masked and a zero tag.
        assert not (tag_is_masked and tag_is_zero)

        if tag_is_masked:
            for b in self.tag_to_groups[tag]:
                bits_orig = set(bits)
                for bit in b:
                    if bit not in bits:
                        bits.add("!" + bit)

                verbose and print(
                    "Grouped %s: %s => %s" %
                    (tag, bits_str(bits_orig), bits_str(bits)))

        if tag_is_zero:
            for bit in self.zero_tag_to_group[tag]:
                bits.add("!" + bit)


def read_segbits(fn_in):
    """
    Reads a segbits file. Removes duplcated lines. Returns a list of the lines.
    """
    lines = []
    llast = None

    with util.OpenSafeFile(fn_in, "r") as f:
        for line in f:
            # Hack: skip duplicate lines
            # This happens while merging a new multibit entry
            line = line.strip()
            if len(line) == 0:
                continue
            if line == llast:
                continue

            lines.append(line)

    return lines


def add_zero_bits(
        fn_in, lines, zero_db, clb_int=False, strict=True, verbose=False):
    '''
    Add multibit entries
    This requires adding some zero bits (ex: !31_09)
    If an entry has any of the
    '''

    zero_groups = ZeroGroups(zero_db)

    new_lines = set()
    changes = 0

    drops = 0

    for line in lines:

        tag, bits, mode, _ = util.parse_db_line(line)

        if bits is not None and mode is None:
            zero_groups.add_tag_bits(tag, bits)

    if verbose:
        zero_groups.print_groups()

    for line in lines:
        tag, bits, mode, _ = util.parse_db_line(line)
        # an enum that needs masking
        # check below asserts that a mask was actually applied
        if mode and mode != "<0 candidates>" and not strict:
            verbose and print("WARNING: dropping unresolved line: %s" % line)
            drops += 1
            continue

        assert mode not in (
            "<const0>",
            "<const1>"), "Entries must be resolved. line: %s" % (line, )

        if mode == "always":
            new_line = line
        else:
            if mode:
                assert mode == "<0 candidates>", line
                bits = set()
            else:
                bits = set(bits)
            """
            This appears to be a large range of one hot interconnect bits
            They are immediately before the first CLB real bits
            """
            if clb_int:
                zero_range(tag, bits, 22, 25)

                set_bits = [bit for bit in bits if bit[0] != '!']
                if len(set_bits) not in [2, 4]:
                    # All INT bits appear to be only have 2 or 4 bits.
                    verbose and print(
                        "WARNING: dropping line with %d bits, not [2, 4]: %s, %s"
                        % (len(set_bits), bits, line))
                    drops += 1
                    continue

            zero_groups.add_bits_from_zero_groups(
                tag, bits, strict=strict, verbose=verbose)

            if strict:
                assert len(bits) > 0, 'Line {} found no bits.'.format(line)
            elif len(bits) == 0:
                verbose and print(
                    "WARNING: dropping unresolved line: %s" % line)
                drops += 1
                continue

            new_line = " ".join([tag] + sorted(bits))

        if re.match(r'.*<.*>.*', new_line):
            print("Original line: %s" % line)
            assert 0, "Failed to remove line mode: %s" % (new_line)

        if new_line != line:
            changes += 1
        new_lines.add(new_line)

    if drops:
        print("WARNING: %s dropped %s unresolved lines" % (fn_in, drops))

    return changes, new_lines


def update_mask(db_root, mask_db, src_dbs, offset=0):
    bits = set()
    mask_db_file = "%s/mask_%s.db" % (db_root, mask_db)

    if os.path.exists(mask_db_file):
        with util.OpenSafeFile(mask_db_file, "r") as f:
            for line in f:
                line = line.split()
                assert len(line) == 2
                assert line[0] == "bit"
                bits.add(line[1])

    for src_db in src_dbs:
        seg_db_file = "%s/segbits_%s.db" % (db_root, src_db)

        if not os.path.exists(seg_db_file):
            continue

        with util.OpenSafeFile(seg_db_file, "r") as f:
            for line in f:
                line = line.split()
                for bit in line[1:]:
                    if bit[0] == "!":
                        continue
                    if offset != 0:
                        m = re.match(r"(\d+)_(\d+)", bit)
                        bit = "%02d_%02d" % (
                            int(m.group(1)), int(m.group(2)) + offset)
                    bits.add(bit)

    if len(bits) > 0:
        with util.OpenSafeFile(mask_db_file, "w") as f:
            for bit in sorted(bits):
                print("bit %s" % bit, file=f)


def load_zero_db(fn):
    # Remove comments and convert to list of lines
    ret = []
    with util.OpenSafeFile(fn, "r") as f:
        for l in f:
            pos = l.find("#")
            if pos >= 0:
                l = l[0:pos]
            l = l.strip()
            if not l:
                continue
            ret.append(l)
    return ret


def remove_ambiguous_solutions(fn_in, db_lines, strict=True, verbose=True):
    """ Removes features with identical solutions.

    During solving, some tags may be tightly coupled and solve to the same
    solution.  In these cases, those solutions must be dropped until
    disambiguating information can be found.
    """
    solutions = {}
    dropped_solutions = set()

    for l in db_lines:
        parts = l.split()
        feature = parts[0]
        bits = frozenset(parts[1:])

        if bits in solutions:
            if strict:
                assert False, "Found solution {} at least twice, in {} and {}".format(
                    bits, feature, solutions[bits])
            else:
                dropped_solutions.add(bits)
        else:
            solutions[bits] = feature

    if strict:
        return 0, db_lines

    drops = 0
    output_lines = set()

    for l in db_lines:
        parts = l.split()
        feature = parts[0]
        bits = frozenset(parts[1:])

        if bits not in dropped_solutions:
            output_lines.add(l)
            drops += 1
        else:
            if verbose:
                print(
                    "WARNING: dropping line due to duplicate solution: %s" % l)

    if drops > 0:
        print("WARNING: %s dropped %s duplicate solutions" % (fn_in, drops))

    return drops, output_lines


def format_bits(tag, bits):
    """ Format tag and bits into line. """
    bit_strs = []
    for bit in sorted(list(bits), key=lambda b: b[1]):
        s = "!" if not bit[0] else ""
        s += "{:02d}_{:02d}".format(bit[1][0], bit[1][1])
        bit_strs.append(s)

    return " ".join([tag] + bit_strs)


def group_tags(lines, tag_groups, bit_groups):
    """
    Implements tag grouping. If a tag belongs to a group then the common bits
    of that group are added to is as zeros.

    >>> tg = [{"A", "B"}]
    >>> bg = [{(1, 2), (3, 4)}]
    >>> res = group_tags({"A 1_2", "B 3_4"}, tg, bg)
    >>> (res[0], sorted(list(res[1])))
    (2, ['A 01_02 !03_04', 'B !01_02 03_04'])

    >>> tg = [{"A", "B"}]
    >>> bg = [{(1, 2), (3, 4)}]
    >>> res = group_tags({"A 1_2", "B 3_4", "C 1_2"}, tg, bg)
    >>> (res[0], sorted(list(res[1])))
    (2, ['A 01_02 !03_04', 'B !01_02 03_04', 'C 01_02'])
    """

    changes = 0
    new_lines = set()

    # Process lines
    for line in lines:

        line = line.strip()
        if not len(line):
            continue

        # Parse the line
        tag, bits, mode, _ = util.parse_db_line(line)
        if not bits:
            bits = set()
        else:
            bits = set([util.parse_tagbit(b) for b in bits])

        # Check if the tag belongs to a group
        for tag_group, bit_group in zip(tag_groups, bit_groups):
            if tag in tag_group:

                # Add zero bits to the tag if not already there
                bit_coords = set([b[1] for b in bits])
                for zero_bit in bit_group:
                    if zero_bit not in bit_coords:
                        bits.add((False, zero_bit))

                # Format the line
                new_line = format_bits(tag, bits)

                # Add the line
                new_lines.add(new_line)
                changes += 1
                break

        # It does not, pass it through unchanged
        else:
            new_lines.add(format_bits(tag, bits))

    return changes, new_lines


def update_seg_fns(
        fn_inouts,
        zero_db,
        tag_groups,
        clb_int,
        lazy=False,
        strict=True,
        verbose=False):

    seg_files = 0
    seg_lines = 0
    for fn_in, fn_out in fn_inouts:
        verbose and print("zb %s: %s" % (fn_in, os.path.exists(fn_in)))
        if lazy and not os.path.exists(fn_in):
            continue

        lines = read_segbits(fn_in)
        changes = 0

        # Find common bits for tag groups
        bit_groups = find_common_bits_for_tag_groups(lines, tag_groups)

        # Group tags
        new_changes, lines = group_tags(lines, tag_groups, bit_groups)
        changes += new_changes

        new_changes, lines = add_zero_bits(
            fn_in,
            lines,
            zero_db,
            clb_int=clb_int,
            strict=strict,
            verbose=verbose)
        changes += new_changes

        new_changes, lines = remove_ambiguous_solutions(
            fn_in,
            lines,
            strict=strict,
            verbose=verbose,
        )
        changes += new_changes

        with util.OpenSafeFile(fn_out, "w") as f:
            for line in sorted(lines):
                print(line, file=f)

        if changes is not None:
            seg_files += 1
            seg_lines += changes
    print(
        "Segbit: checked %u files w/ %u changed lines" %
        (seg_files, seg_lines))


def update_masks(db_root):
    for mask_db, src_dbs in [
        ("clbll_l", ("clbll_l", "int_l")),
        ("clbll_r", ("clbll_r", "int_r")),
        ("clblm_l", ("clblm_l", "int_l")),
        ("clblm_r", ("clblm_r", "int_r")),
        ("hclk_l", ("hclk_l", )),
        ("hclk_r", ("hclk_r", )),
        ("bram_l", ("bram_l", )),
        ("bram_r", ("bram_r", )),
        ("dsp_l", ("dsp_l", )),
        ("dsp_r", ("dsp_r", )),
    ]:
        update_mask(db_root, mask_db, src_dbs)

    for mask_db, src_dbs in [
        ("bram_l", ("int_l", )),
        ("bram_r", ("int_r", )),
        ("dsp_l", ("int_l", )),
        ("dsp_r", ("int_r", )),
    ]:
        for k in range(5):
            update_mask(db_root, mask_db, src_dbs, offset=64 * k)

    print("Mask: checked files")


def update_segs(
        db_root,
        clb_int,
        seg_fn_in,
        seg_fn_out,
        zero_db_fn,
        tag_groups,
        strict=True,
        verbose=False):
    if clb_int:
        zero_db = clb_int_zero_db
        lazy = True

        def gen_fns():
            for tile_type in ["int_l", "int_r", "clbll_l", "clbll_r",
                              "clblm_l", "clblm_r"]:
                fn = "%s/segbits_%s.db" % (db_root, tile_type)
                yield (fn, fn)

        fn_inouts = list(gen_fns())
    else:
        assert seg_fn_in
        assert zero_db_fn
        lazy = False

        if not seg_fn_out:
            seg_fn_out = seg_fn_in

        fn_inouts = [(seg_fn_in, seg_fn_out)]
        zero_db = load_zero_db(zero_db_fn)
    print("CLB INT mode: %s" % clb_int)
    print("Segbit groups: %s" % len(zero_db))
    update_seg_fns(
        fn_inouts,
        zero_db,
        tag_groups,
        clb_int,
        lazy=lazy,
        strict=strict,
        verbose=verbose)


def find_common_bits_for_tag_groups(lines, tag_groups):
    """
    For each tag group finds a common set of bits that have value of one.
    """

    bit_groups = []

    for tag_group in tag_groups:
        bit_group = set()

        for line in lines:
            tag, bits, mode, _ = util.parse_db_line(line)
            if not bits:
                continue

            bits = set([util.parse_tagbit(b) for b in bits])

            if tag in tag_group and len(bits):
                ones = set([b[1] for b in bits if b[0]])
                bit_group |= ones

        bit_groups.append(bit_group)

    return bit_groups


def load_tag_groups(file_name):
    """
    Loads tag groups from a text file.

    A tag group is defined by specifying a space separated list of tags within
    a single line. Lines that are empty or start with '#' are ignored.
    """
    tag_groups = []

    # Load tag group specifications
    with util.OpenSafeFile(file_name, "r") as fp:
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


def run(
        db_root,
        clb_int=False,
        zero_db_fn=None,
        seg_fn_in=None,
        seg_fn_out=None,
        groups_fn_in=None,
        strict=None,
        verbose=False):

    if strict is None:
        strict = not clb_int

    # Load tag groups
    tag_groups = []
    if groups_fn_in is not None:
        tag_groups = load_tag_groups(groups_fn_in)

    # Probably should split this into two programs
    update_segs(
        db_root,
        clb_int=clb_int,
        seg_fn_in=seg_fn_in,
        seg_fn_out=seg_fn_out,
        zero_db_fn=zero_db_fn,
        tag_groups=tag_groups,
        strict=strict,
        verbose=verbose)
    if clb_int:
        update_masks(db_root)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Create multi-bit entries')

    util.db_root_arg(parser)
    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument(
        '--clb-int', action='store_true', help='Fixup CLB interconnect')
    parser.add_argument('--zero-db', help='Apply custom patches')
    parser.add_argument('--seg-fn-in', help='')
    parser.add_argument('--seg-fn-out', help='')
    util.add_bool_arg(parser, "--strict", default=False)

    parser.add_argument(
        "-g",
        "--groups",
        type=str,
        default=None,
        help="Input tag group definition file")

    args = parser.parse_args()

    run(
        args.db_root,
        args.clb_int,
        args.zero_db,
        args.seg_fn_in,
        args.seg_fn_out,
        args.groups,
        strict=args.strict,
        verbose=args.verbose)


if __name__ == '__main__':
    main()
