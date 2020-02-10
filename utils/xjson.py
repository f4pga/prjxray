#!/usr/bin/env python3
import io
import json
import re
import sys

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
    # FIXME: We assume that a list is a tileconn.json format...
    if isinstance(data, list) and len(data) > 0 and 'wire_pairs' in data[0]:
        for o in data:
            o['wire_pairs'].sort(
                key=lambda o: (extract_numbers(o[0]), extract_numbers(o[1])))

        data.sort(key=lambda o: (o['tile_types'], o['grid_deltas']))
    else:

        def key(o):
            if o is None:
                return None
            elif isinstance(o, str):
                return extract_numbers(o)
            elif isinstance(o, int):
                return o
            elif isinstance(o, list):
                return [key(i) for i in o]
            elif isinstance(o, dict):
                return [(key(k), key(v)) for k, v in o.items()]
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

            elif isinstance(o, list):
                if len(o) == 2:
                    return o

                nlist = []
                for i in o:
                    nlist.append((key(i), rsorter(i)))
                nlist.sort(key=lambda n: n[0])

                new_list = []
                for _, i in nlist:
                    new_list.append(i)
                return new_list
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
