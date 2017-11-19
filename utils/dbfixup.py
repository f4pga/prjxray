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

def update_mask(mask_db, *src_dbs):
    bits = set()
    with open("%s/%s/mask_%s.db" % (os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"), mask_db), "r") as f:
        for line in f:
            line = line.split()
            assert len(line) == 2
            assert line[0] == "bit"
            bits.add(line[1])
    for src_db in src_dbs:
        with open("%s/%s/segbits_%s.db" % (os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"), src_db), "r") as f:
            for line in f:
                line = line.split()
                for bit in line[1:]:
                    if bit[0] != "!":
                        bits.add(bit)
    with open("%s/%s/mask_%s.db" % (os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"), mask_db), "w") as f:
        for bit in sorted(bits):
            print("bit %s" % bit, file=f)

add_zero_bits("int_l")
add_zero_bits("int_r")

update_mask("clbll_l", "clbll_l", "int_l")
update_mask("clbll_r", "clbll_r", "int_r")
update_mask("clblm_l", "clblm_l", "int_l")
update_mask("clblm_r", "clblm_r", "int_r")

