#/usr/bin/env python3

import sys, os, re

def add_zero_bits(tile_type):
    assert os.getenv("XRAY_DATABASE") == "artix7"
    dbfile = "%s/%s/segbits_%s.db" % (os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"), tile_type)
    new_lines = set()
    with open(dbfile, "r") as f:
        for line in f:
            line = line.split()
            tag = line[0]
            bits = set(line[1:])
            bitidx = None
            for bit in bits:
                if bit[0] == "!":
                    continue
                fidx, bidx = [int(s) for s in bit.split("_")]
                if 22 <= fidx <= 25:
                    bitidx = bidx
            if bitidx is not None:
                for fidx in range(22, 26):
                    bit = "%02d_%02d" % (fidx, bitidx)
                    if bit not in bits:
                        bits.add("!" + bit)
            new_lines.add(" ".join([tag] + sorted(bits)))
    with open(dbfile, "w") as f:
        for line in sorted(new_lines):
            print(line, file=f)

add_zero_bits("int_l")
add_zero_bits("int_r")

