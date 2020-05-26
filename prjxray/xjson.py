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
import io
import json
import re

from collections import OrderedDict


def extract_numbers(s):
    """
    >>> extract_numbers("CLK_HROW_WR10END2_3")
    ('CLK_HROW_WR', 10, 'END', 2, '_', 3)
    >>> extract_numbers("VBRK_WR1END2")
    ('VBRK_WR', 1, 'END', 2)
    """
    bits = []
    for m in re.finditer("([^0-9]*)([0-9]*)", s):
        if m.group(1):
            bits.append(m.group(1))
        if m.group(2):
            bits.append(int(m.group(2)))
    return tuple(bits)


def sort(data):
    """Sort data types via "natural" numbers.

    Supports all the basic Python data types.
    >>> o = sort({
    ...    't1': {'c','b'},          # Set
    ...    't2': ('a2', 'a10', 'e'), # Tuple
    ...    't3': [5, 3, 2],          # List
    ...    't4': {                   # Dictionary
    ...        'a4': ('b2', 'b3'),
    ...        'a2': ['c1', 'c2', 'c0', 'c10'],
    ...    },
    ...    't5': ['a1b5', 'a2b1', 'a1b1'],
    ... })
    >>> for t in o:
    ...    print(t+':', o[t])
    t1: ('b', 'c')
    t2: ('a2', 'a10', 'e')
    t3: (5, 3, 2)
    t4: OrderedDict([('a2', ('c1', 'c2', 'c0', 'c10')), ('a4', ('b2', 'b3'))])
    t5: ('a1b5', 'a2b1', 'a1b1')

    Don't mangle "pairs"
    >>> sort([('b', 'c'), ('2', '1')])
    (('b', 'c'), ('2', '1'))
    """

    def key(o):
        if o is None:
            return None
        elif isinstance(o, str):
            return extract_numbers(o)
        elif isinstance(o, int):
            return o
        elif isinstance(o, (list, tuple)):
            return tuple(key(i) for i in o)
        elif isinstance(o, dict):
            return tuple((key(k), key(v)) for k, v in o.items())
        elif isinstance(o, set):
            return tuple(key(k) for k in o)
        raise ValueError(repr(o))

    def rsorter(o):
        if isinstance(o, dict):
            nitems = []
            for k, v in o.items():
                nitems.append((key(k), k, rsorter(v)))
            nitems.sort(key=lambda n: n[0])

            new_dict = OrderedDict()
            for _, k, v in nitems:
                new_dict[k] = v
            return new_dict

        elif isinstance(o, set):
            return tuple(sorted((rsorter(v) for v in o), key=key))
        elif isinstance(o, (tuple, list)):
            return tuple(rsorter(v) for v in o)
        else:
            return o

    return rsorter(data)


def pprint(f, data):
    detach = False
    if not isinstance(f, io.TextIOBase):
        detach = True
        f = io.TextIOWrapper(f)
    data = sort(data)
    json.dump(data, f, indent=4)
    f.write('\n')
    f.flush()
    if detach:
        f.detach()
