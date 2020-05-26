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
Python 3 removed the 'cmp' function and raises a Type error when you try to
compare different types. This module recreates Python 2 style 'cmp' function
which produces a "total ordering" for mixed type lists.
"""

import functools
import itertools


def cmp(a, b):
    """

    >>> cmp(1, 1)
    0
    >>> cmp('A', 'A')
    0
    >>> cmp(None, None)
    0
    >>> cmp(('A', 'B'), ('A', 'B'))
    0
    >>> cmp(['A', 'B'], ('A', 'B'))
    0
    >>> cmp((1, 2), (1, 2))
    0
    >>> cmp((1, 2), [1, 2])
    0

    >>> cmp(1, 2)
    -1
    >>> cmp('A', 'B')
    -1
    >>> cmp(('A', 'B'), ('A', 'C'))
    -1
    >>> cmp(['A', 'B'], ('A', 'C'))
    -1
    >>> cmp((1, 2), (1, 3))
    -1
    >>> cmp((1, 2), [1, 3])
    -1

    >>> cmp(2, 1)
    1
    >>> cmp('B', 'A')
    1
    >>> cmp(('A', 'C'), ('A', 'B'))
    1
    >>> cmp(['A', 'C'], ('A', 'B'))
    1
    >>> cmp((1, 3), (1, 2))
    1
    >>> cmp((1, 3), [1, 2])
    1

    >>> cmp(1, None)
    1
    >>> cmp('A', None)
    1
    >>> cmp(('A', 'B'), None)
    1
    >>> cmp(['A', 'B'], None)
    1
    >>> cmp((1, 2), None)
    1
    >>> cmp((1, 2), None)
    1

    >>> cmp(None, 2)
    -1
    >>> cmp(None, 'B')
    -1
    >>> cmp(None, ('A', 'B'))
    -1
    >>> cmp(None, ('A', 'C'))
    -1
    >>> cmp(None, (1, 2))
    -1
    >>> cmp(None, [1, 3])
    -1

    >>> cmp(1, 'A')
    -1
    >>> cmp('A', 1)
    1

    >>> cmp(('A', 'B'), 1)
    1
    >>> cmp(1, ['A', 'B'])
    -1

    >>> cmp((1, 2), 1)
    1
    >>> cmp(1, (1, 2))
    -1

    >>> cmp('A', 'AA')
    -1
    >>> cmp('AA', 'A')
    1

    >>> cmp(b'A', b'A')
    0
    >>> cmp(b'A', b'AA')
    -1
    >>> cmp(b'AA', b'A')
    1

    >>> def bit(*args):
    ...   return args
    >>> a = ('CLBLL', 'L', 'SLICEL', ('X', 0), 'AFFMUX', 'XOR')
    >>> b = ('CLBLL', 'L', 'SLICEL', ('X', 0), 'AFFMUX', ('F', 7))
    >>> cmp(a, b)
    -1
    >>> cmp(b, a)
    1

    """
    if not isinstance(a, (str, bytes)) and not isinstance(b, (str, bytes)):
        try:
            for i, j in itertools.zip_longest(iter(a), iter(b)):
                r = cmp(i, j)
                if r != 0:
                    return r
            return 0
        except TypeError:
            pass
    if type(a) == type(b):
        if a == b:
            return 0
        elif a < b:
            return -1
        elif a > b:
            return 1
        else:
            raise SystemError
    return cmp(a.__class__.__name__, b.__class__.__name__)


cmp_key = functools.cmp_to_key(cmp)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
