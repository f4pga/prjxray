#!/usr/bin/env python3
import io
import json
import re
import sys


def extract_numbers(s):
    """
    >>> extract_numbers("CLK_HROW_WR10END2_3")
    ('CLK_HROW_WR', 10, 'END', 2, '_', 3)
    >>> extract_numbers("VBRK_WR1END2")
    ('VBRK_WR', 1, 'END', 2)
    """
    bits = []
    for m in re.finditer("([^0-9]*)([0-9]*)",s):
        if m.group(1):
            bits.append(m.group(1))
        if m.group(2):
            bits.append(int(m.group(2)))
    return tuple(bits)


def sort(data):
    # FIXME: We assume that a list is a tileconn.json format...
    if isinstance(data, list):
        for o in data:
            o['wire_pairs'].sort(key=lambda o: (extract_numbers(o[0]), extract_numbers(o[1])))

        data.sort(key=lambda o: (o['tile_types'], o['grid_deltas']))
    else:
        def walker(o, f):
            if isinstance(o, dict):
                for i in o.values():
                    walker(i, f)
            elif isinstance(o, list):
                for i in o:
                    walker(i, f)
            f(o)

        def f(o):
            if isinstance(o, list):
                if len(o) > 2:
                    strings = all(isinstance(x, str) for x in o)
                    if strings:
                        o.sort()

        walker(data, f)


def pprint(f, data):
    detach = False
    if not isinstance(f, io.TextIOBase):
        detach = True
        f = io.TextIOWrapper(f)
    sort(data)
    json.dump(data, f, sort_keys=True, indent=4)
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
