#!/usr/bin/env python3

import sys
import re

database = dict()
database_r = dict()

for arg in sys.argv[1:]:
    with open(arg, "r") as f:
        for line in f:
            if "<" in line:
                raise Exception("Found '<' in this line: %s" % line)

            line = line.split()
            key = line[0]
            bits = tuple(sorted(set(line[1:])))

            if key in database:
                print("Warning: Duplicate key: %s %s" % (key, bits))

            if bits in database_r:
                print("Warning: Duplicate bits: %s %s" % (key, bits))

            database[key] = bits
            database_r[bits] = key


def get_subsets(bits):
    retval = list()
    retval.append(bits)
    for i in range(len(bits)):
        for s in get_subsets(bits[i + 1:]):
            retval.append(bits[0:i] + s)
    return retval


def check_subsets(bits):
    for sub_bits in sorted(get_subsets(bits)):
        if sub_bits != bits and sub_bits != ():
            if sub_bits in database_r:
                print("Warning: Entry %s %s is a subset of entry %s %s." %
                      (database_r[sub_bits], sub_bits, database_r[bits], bits))


for key, bits in database.items():
    check_subsets(bits)
