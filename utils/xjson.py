#!/usr/bin/env python3
import io
import json
import re
import sys

from collections import OrderedDict, defaultdict
from ordered_set import OrderedSet


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

    Don't mangle "pairs"
    >>> sort(('b', 'c'))
    ('b', 'c')
    >>> sort(('2', '1'))
    ('2', '1')
    >>> sort(['b', '2'])
    ('b', '2')
    >>> sort([('b', 'c'), ('2', '1')])
    (('2', '1'), ('b', 'c'))

    >>> o = sort({
    ...    't1': {'c','b'},          # Set
    ...    't2': ('a2', 'a10', 'e'), # Tuple
    ...    't3': {                   # Dictionary
    ...        'a4': ('b2', 'b3'),
    ...        'a2': ['c1', 'c2', 'c0', 'c10'],
    ...    },
    ...    't4': ['a1b5', 'a2b1', 'a1b1'],
    ...    't5': [5, 3, 2],          # List
    ...    't6': [5.0, 3.0, 2.0],    # List
    ...    't6': [5, 3.0, 2.0],      # List
    ... })
    >>> for t in o:
    ...    print(t+':', o[t])
    t1: OrderedSet(['b', 'c'])
    t2: ('a2', 'a10', 'e')
    t3: OrderedDict([('a2', ('c0', 'c1', 'c2', 'c10')), ('a4', ('b2', 'b3'))])
    t4: ('a1b1', 'a1b5', 'a2b1')
    t5: (5, 3, 2)
    t6: (5, 3.0, 2.0)

    """
    def key(o):
        if o is None:
            return None
        elif isinstance(o, str):
            o = extract_numbers(o)
            # Convert numbers back to strings with lots of leading zeros so
            # Python3 can sort them
            n = []
            for i in o:
                if not i:
                    n.append('')
                elif type(i) == int:
                    n.append("{:10d}".format(i))
                else:
                    n.append(i)
            return tuple(n)
        elif isinstance(o, (int, float)):
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
            nitems = []
            for k in o:
                nitems.append((key(k), k))
            nitems.sort(key=lambda n: n[0])

            new_set = OrderedSet()
            for _, k in nitems:
                new_set.add(k)
            return new_set

        elif isinstance(o, (tuple, list)):
            nlist = []
            ntypes = defaultdict(lambda: 0)
            for v in o:
                ntypes[type(v)] += 1
                nlist.append((key(v), rsorter(v)))

            # FIXME: These are gross hacks!
            # Ignore pairs of strings
            if len(nlist) == 2 and ntypes[str] == 2:
                return tuple(o)
            # Ignore lists of numbers
            if ntypes[int]+ntypes[float] == len(nlist):
                return tuple(o)

            nlist.sort(key=lambda n: n[0])

            new_list = []
            for _, v in nlist:
                new_list.append(v)
            return tuple(new_list)
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


if __name__ == "__main__":
    if len(sys.argv) == 1:
        import doctest
        doctest.testmod()
    else:
        assert len(sys.argv) == 2
        d = json.load(open(sys.argv[1]))
        pprint(sys.stdout, d)
