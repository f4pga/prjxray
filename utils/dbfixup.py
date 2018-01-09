#/usr/bin/env python3

import sys
import os
import re

zero_db = [
    "00_21 00_22 00_26 01_28|00_25 01_20 01_21 01_24",
    "00_23 00_30 01_22 01_25|00_27 00_29 01_26 01_29",
    "01_12 01_14 01_16 01_18|00_10 00_11 01_09 01_10",
    "00_13 01_17 00_15 00_17|00_18 00_19 01_13 00_14",
    "00_34 00_38 01_33 01_37|00_35 00_39 01_38 01_40",
    "00_33 00_41 01_32 01_34|00_37 00_42 01_36 01_41",

    # CLBL?_?.SLICE?_X?.?FF.DMUX
    "30_00 30_01 30_02 30_03",
    "30_24 30_25 30_26 30_27",
    "30_35 30_36 30_37 30_38",
    "30_59 30_60 30_61 30_62",
    "30_04 31_00 31_01 31_02",
    "31_24 31_25 31_26 31_27",
    "31_35 31_36 31_37 31_38",
    "30_58 31_60 31_61 31_62",

    # CLBL?_?.SLICE?_X?.?MUX
    "30_06 30_07 30_08 30_11",
    "30_20 30_21 30_22 30_23",
    "30_40 30_43 30_44 30_45",
    "30_51 30_52 30_56 30_57",
    "30_05 31_07 31_09 31_10",
    "30_28 30_29 31_20 31_21",
    "30_41 30_42 31_40 31_43",
    "30_53 31_53 31_56 31_57",
]


def add_zero_bits(tile_type):
    assert os.getenv("XRAY_DATABASE") in ["artix7", "kintex7"]
    dbfile = "%s/%s/segbits_%s.db" % (os.getenv("XRAY_DATABASE_DIR"),
                                      os.getenv("XRAY_DATABASE"), tile_type)
    new_lines = set()
    llast = None

    if not os.path.exists(dbfile):
        return

    with open(dbfile, "r") as f:
        for line in f:
            # Hack: skip duplicate lines
            # This happens while merging a new multibit entry
            if line == llast:
                continue
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
                if "|" in zdb:
                    a, b = zdb.split("|")
                    a = a.split()
                    b = b.split()
                else:
                    a = zdb.split()
                    b = a
                match = False
                for bit in a:
                    if bit in bits:
                        match = True
                if match:
                    for bit in b:
                        if bit not in bits:
                            bits.add("!" + bit)
            new_lines.add(" ".join([tag] + sorted(bits)))
            llast = line

    with open(dbfile, "w") as f:
        for line in sorted(new_lines):
            print(line, file=f)


def update_mask(mask_db, *src_dbs):
    bits = set()
    mask_db_file = "%s/%s/mask_%s.db" % (
        os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"), mask_db)

    if os.path.exists(mask_db_file):
        with open(mask_db_file, "r") as f:
            for line in f:
                line = line.split()
                assert len(line) == 2
                assert line[0] == "bit"
                bits.add(line[1])

    for src_db in src_dbs:
        seg_db_file = "%s/%s/segbits_%s.db" % (
            os.getenv("XRAY_DATABASE_DIR"), os.getenv("XRAY_DATABASE"), src_db)

        if not os.path.exists(seg_db_file):
            continue

        with open(seg_db_file, "r") as f:
            for line in f:
                line = line.split()
                for bit in line[1:]:
                    if bit[0] != "!":
                        bits.add(bit)

    if len(bits) > 0:
        with open(mask_db_file, "w") as f:
            for bit in sorted(bits):
                print("bit %s" % bit, file=f)


add_zero_bits("int_l")
add_zero_bits("int_r")
add_zero_bits("clbll_l")
add_zero_bits("clbll_r")
add_zero_bits("clblm_l")
add_zero_bits("clblm_r")

update_mask("clbll_l", "clbll_l", "int_l")
update_mask("clbll_r", "clbll_r", "int_r")
update_mask("clblm_l", "clblm_l", "int_l")
update_mask("clblm_r", "clblm_r", "int_r")
update_mask("hclk_l", "hclk_l")
update_mask("hclk_r", "hclk_r")

for k in range(5):
    update_mask("bram%d_l" % k, "bram%d_l" % k, "int_l")
    update_mask("bram%d_r" % k, "bram%d_r" % k, "int_r")
    update_mask("dsp%d_l" % k, "dsp%d_l" % k, "int_l")
    update_mask("dsp%d_r" % k, "dsp%d_r" % k, "int_r")
