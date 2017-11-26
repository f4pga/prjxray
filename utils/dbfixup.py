#/usr/bin/env python3

import sys, os, re

zero_db = [
    "00_21 00_22 00_26 01_28|00_25 01_20 01_21 01_24",
    "00_23 00_30 01_22 01_25|00_27 00_29 01_26 01_29",
    "01_12 01_14 01_16 01_18|00_10 00_11 01_09 01_10",
    "00_13 01_17 00_15 00_17|00_18 00_19 01_13 00_14",
    "00_34 00_38 01_33 01_37|00_35 00_39 01_38 01_40",
    "00_33 00_41 01_32 01_34|00_37 00_42 01_36 01_41",
]

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
            for zdb in zero_db:
                a, b = zdb.split("|")
                a = a.split()
                b = b.split()
                match = False
                for bit in a:
                    if bit in bits:
                        match = True
                if match:
                    for bit in b:
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

