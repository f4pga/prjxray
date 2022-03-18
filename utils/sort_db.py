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
Canonicalize the Project X-Ray database files by sorting. The aim is to reduce
the diff output between runs to make it clearer what has changed.

DB Files
--------

DB files are sorted into "natural" ordering. This is generally the order that a
human would sort them in rather than how they sort as ASCII strings.

For example with tags, a sequence of ABC1 to ABC12 would have the ASCII sort
order of;

    ABC1
    ABC10
    ABC11
    ABC12
    ABC2
    ...
    ABC9

We instead sort them like the following;

    ABC1
    ABC2
    ...
    ABC9
    ABC10
    ABC11
    ABC12

For the segbit files, we sort the bit definitions ignoring any leading
exclamation mark. Doing this generally makes it much easier to see patterns in
the bit descriptions and you end up with output like the following for 1-hot
encoded choices,

    ABC.CHOICE1 22_15 !22_16 !22_17
    ABC.CHOICE2 !22_15 22_16 !22_17
    ABC.CHOICE3 !22_15 !22_16 22_17

JSON Files
----------

For the JSON files, we run them through Python's pretty printing module and
sort sets (lists where the order doesn't matter).

"""

import csv
import os
import random
import re
import sys

import json
import utils.xjson as xjson
import utils.cmp as cmp

from prjxray.util import OpenSafeFile

def split_all(s, chars):
    """Split on multiple character values.

    >>> split_all('a_b_c_d', '_. ')
    ['a', 'b', 'c', 'd']
    >>> split_all('a b c d', '_. ')
    ['a', 'b', 'c', 'd']
    >>> split_all('a.b.c.d', '_. ')
    ['a', 'b', 'c', 'd']
    >>> split_all('a_b.c d', '_. ')
    ['a', 'b', 'c', 'd']
    >>> split_all('a b_c.d', '_. ')
    ['a', 'b', 'c', 'd']
    """
    chars = list(chars)

    o = [s]
    while len(chars) > 0:
        c = chars.pop(0)

        n = []
        for i in o:
            n += i.split(c)

        o = n
    return o


NUM_REGEX = re.compile('^(.*?)([0-9]*)$')


def extract_num(i):
    """Extract number from a string to be sorted.

    >>> extract_num('BLAH123')
    ('BLAH', 123)
    >>> extract_num('123')
    123
    >>> extract_num('BLAH')
    'BLAH'
    >>> extract_num('')
    ''
    """
    g = NUM_REGEX.match(i).groups()
    if len(g[-1]) == 0:
        return i
    i = int(g[-1])
    if len(g[0]) == 0:
        return i
    else:
        return (g[0], i)


class bit(tuple):
    """Class representing a bit specifier.

    >>> a = bit.parse("02_12")
    >>> a
    bit(2, 12, True)
    >>> b = bit.parse("!02_03")
    >>> b
    bit(2, 3, False)
    >>> b == a
    False
    >>> b < a
    True
    >>> str(a)
    '02_12'
    >>> str(b)
    '!02_03'

    >>> bit.parseline("!30_04 !31_00 !31_01 31_02")
    [bit(30, 4, False), bit(31, 0, False), bit(31, 1, False), bit(31, 2, True)]

    >>> bit.parseline("31_02 !31_00 !31_01 !30_04")
    [bit(30, 4, False), bit(31, 0, False), bit(31, 1, False), bit(31, 2, True)]
    """

    @classmethod
    def parse(cls, s):
        mode = s[0] != '!'
        s = s.replace('!', '')
        assert '_' in s, s
        a, b = s.split('_', 1)
        assert '_' not in b, s
        return cls((extract_num(a), extract_num(b), mode))

    @classmethod
    def parseline(cls, s):
        bits = [cls.parse(b) for b in s.split(' ')]
        bits.sort()
        return bits

    def __repr__(self):
        return "bit" + tuple.__repr__(self)

    def __str__(self):
        s = self
        return "{}{:02d}_{:02d}".format(['!', ''][s[2]], s[0], s[1])


def convert_bit(i):
    """Convert a bit pattern into sortable form.

    >>> convert_bit("02_12")
    bit(2, 12, True)
    >>> convert_bit("!02_12")
    bit(2, 12, False)
    >>> convert_bit("!02_02")
    bit(2, 2, False)
    >>> convert_bit("always")
    'always'
    """
    if '_' not in i:
        return i
    return bit.parse(i)


def segbit_line_sort_bits(l):
    """Sort the bit section of a segbit line.

    >>> segbit_line_sort_bits("A !28_35 !27_39 27_37")
    'A 27_37 !27_39 !28_35'

    >>> segbit_line_sort_bits("B !28_35 !27_39 !27_37")
    'B !27_37 !27_39 !28_35'

    >>> segbit_line_sort_bits("C 28_35 00_00 !27_37")
    'C 00_00 !27_37 28_35'

    """
    tag, *segbits = l.split()

    segbits = [bit.parse(b) for b in segbits]
    segbits.sort()

    return "{} {}".format(tag, " ".join(str(s) for s in segbits))


def sortable_tag(t):
    """
    >>> sortable_tag("CLBLL_L.CLBLL_L_A.CLBLL_L_A1")
    ('CLBLL', 'L', 'CLBLL', 'L', 'A', 'CLBLL', 'L', ('A', 1))

    >>> sortable_tag("CLBLL_L.CLBLL_LOGIC_OUTS23.CLBLL_LL_DMUX")
    ('CLBLL', 'L', 'CLBLL', 'LOGIC', ('OUTS', 23), 'CLBLL', 'LL', 'DMUX')

    >>> sortable_tag("BRAM_L.RAMB18_Y0.INIT_B[9]")
    ('BRAM', 'L', ('RAMB', 18), ('Y', 0), 'INIT', 'B', 9)

    >>> sortable_tag("BRAM_L.RAMB18_Y0.READ_WIDTH_A_18")
    ('BRAM', 'L', ('RAMB', 18), ('Y', 0), 'READ', 'WIDTH', 'A', 18)
    """
    return tuple(extract_num(i) for i in split_all(t, '_.[]') if i != '')


def sortable_line_from_mask(l):
    """Convert a line in a mask_XXXX.db file to something sortable.

    Example lines from mask_XXX.db file
    >>> a, b = sortable_line_from_mask("bit 00_00")
    >>> a
    bit(0, 0, True)
    >>> b
    'bit 00_00'

    >>> a, b = sortable_line_from_mask("bit 09_39")
    >>> a
    bit(9, 39, True)
    >>> b
    'bit 09_39'
    """
    tag, b = l.split(' ', 1)
    assert tag == 'bit', tag
    return bit.parse(b), l


def sortable_line_from_ppips(l):
    """Convert a line in a ppips_XXX.db file to something sortable.

    Example lines from ppips_XXX.db file
    >>> a, b = sortable_line_from_ppips("CLBLL_L.CLBLL_L_A.CLBLL_L_A1 hint")
    >>> a
    (('CLBLL', 'L', 'CLBLL', 'L', 'A', 'CLBLL', 'L', ('A', 1)), 'hint')
    >>> b
    'CLBLL_L.CLBLL_L_A.CLBLL_L_A1 hint'

    >>> a, b = sortable_line_from_ppips("CLBLL_L.CLBLL_LOGIC_OUTS23.CLBLL_LL_DMUX always")
    >>> a
    (('CLBLL', 'L', 'CLBLL', 'LOGIC', ('OUTS', 23), 'CLBLL', 'LL', 'DMUX'), 'always')
    >>> b
    'CLBLL_L.CLBLL_LOGIC_OUTS23.CLBLL_LL_DMUX always'
    """
    assert ' ' in l, repr(l)
    tag, ptype = l.split(' ', 1)
    tag = sortable_tag(tag)
    return (tag, ptype), l


def sortable_line_from_segbits(l):
    """Convert a line in segbits_XXX.db file to something sortable.

    >>> (tag, bits), b = sortable_line_from_segbits("BRAM_L.RAMB18_Y0.INIT_B[9] 27_15")
    >>> tag
    ('BRAM', 'L', ('RAMB', 18), ('Y', 0), 'INIT', 'B', 9)
    >>> bits
    (bit(27, 15, True),)
    >>> b
    'BRAM_L.RAMB18_Y0.INIT_B[9] 27_15'

    >>> (tag, bits), b = sortable_line_from_segbits("BRAM_L.RAMB18_Y0.READ_WIDTH_A_18 !28_35 !27_39 27_37")
    >>> tag
    ('BRAM', 'L', ('RAMB', 18), ('Y', 0), 'READ', 'WIDTH', 'A', 18)
    >>> bits
    (bit(27, 37, True), bit(27, 39, False), bit(28, 35, False))
    >>> b
    'BRAM_L.RAMB18_Y0.READ_WIDTH_A_18 27_37 !27_39 !28_35'
    """
    tag, sbit = l.split(' ', 1)
    tag = sortable_tag(tag)

    bits = bit.parseline(sbit)

    l = segbit_line_sort_bits(l)
    return (tag, tuple(bits)), l


def sortable_line_from_origin_segbits(l):
    tag, origin, sbit = l.split(' ', 2)
    tag = sortable_tag(tag)

    bits = bit.parseline(sbit)

    return (tag, tuple(bits)), l


def sort_db(pathname):
    """Sort a XXX.db file."""
    filename = os.path.split(pathname)[-1]
    if filename.startswith('segbits_'):
        if 'origin_info' in filename:
            sortable_line_from_dbfile = sortable_line_from_origin_segbits
        else:
            sortable_line_from_dbfile = sortable_line_from_segbits
    elif 'origin_info' in filename:
        return False
    elif filename.startswith('ppips_'):
        sortable_line_from_dbfile = sortable_line_from_ppips
    elif filename.startswith('grid-'):
        sortable_line_from_dbfile = sortable_line_from_ppips
    elif filename.startswith('mask_'):
        sortable_line_from_dbfile = sortable_line_from_mask
    else:
        return False

    with OpenSafeFile(pathname) as f:
        lines = f.readlines()

    tosort = []
    for l in lines:
        l = l.strip()
        if not l:
            continue
        tosort.append(sortable_line_from_dbfile(l))

    tosort.sort(key=cmp.cmp_key)

    with open(pathname, 'w') as f:
        for _, l in tosort:
            f.write(l)
            f.write('\n')

    return True


def sort_csv(pathname):
    rows = []
    fields = []
    delimiter = None
    with open(pathname, newline='') as f:
        if pathname.endswith('.csv'):
            delimiter = ','
        elif pathname.endswith('.txt'):
            delimiter = ' '
        reader = csv.DictReader(f, delimiter=delimiter)
        fields.extend(reader.fieldnames)
        rows.extend(reader)
        del reader

    def sort_key(r):
        v = []
        for field in fields:
            v.append(sortable_tag(r[field]))
        return tuple(v)

    rows.sort(key=sort_key)

    with open(pathname, 'w', newline='') as f:
        writer = csv.DictWriter(
            f, fields, delimiter=delimiter, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)

    return True


def sort_json(filename):
    """Sort a XXX.json file."""

    try:
        with OpenSafeFile(filename) as f:
            d = json.load(f)
    except json.JSONDecodeError as e:
        print(e)
        return False

    with OpenSafeFile(filename, 'w') as f:
        xjson.pprint(f, d)

    return True


def sort_db_text(n):
    rows = []
    with OpenSafeFile(n) as f:
        for l in f:
            rows.append(([extract_num(s) for s in l.split()], l))

    rows.sort(key=lambda i: i[0])

    with OpenSafeFile(n, 'w') as f:
        for l in rows:
            f.write(l[-1])

    return True


def sort_file(n):

    assert os.path.exists(n)

    base, ext = os.path.splitext(n)
    dirname, base = os.path.split(base)

    # Leave db files with fuzzer of origin untouched
    if "origin_info" in n and not base.startswith('segbits'):
        print("Ignoring     file {:45s}".format(n), flush=True)
        return

    if ext == '.db':
        print("Sorting DB   file {:45s}".format(n), end=" ", flush=True)
        x = sort_db(n)
    elif ext == '.json':
        print("Sorting JSON file {:45s}".format(n), end=" ", flush=True)
        x = sort_json(n)
    elif ext in ('.csv', '.txt'):
        if n.endswith('-db.txt'):
            print("Sorting txt  file {:45s}".format(n), end=" ", flush=True)
            x = sort_db_text(n)
        else:
            print("Sorting CSV  file {:45s}".format(n), end=" ", flush=True)
            x = sort_csv(n)
    else:
        print("Ignoring     file {:45s}".format(n), end=" ", flush=True)
        x = True
    if x:
        print(".. success.")
    else:
        print(".. failed.")


def sort_dir(dirname):
    for n in sorted(os.listdir(dirname)):
        n = os.path.join(dirname, n)
        if os.path.isdir(n):
            print("Entering     dir  {:45s}".format(n), flush=True)
            sort_dir(n)
            continue
        elif not os.path.isfile(n):
            print("Ignoring non-file {:45s}".format(n), flush=True)
            continue

        sort_file(n)


def main(argv):
    if argv[1:]:
        for n in argv[1:]:
            sort_file(n)
    else:
        sort_dir('.')
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
