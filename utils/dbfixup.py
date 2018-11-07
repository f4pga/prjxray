#/usr/bin/env python3

import sys, os, re
from prjxray import util

clb_int_zero_db = [
    # CLB interconnet
    # Ex:
    # segbits_hclk_l.db:73:HCLK_L.HCLK_LEAF_CLK_B_BOTL4.HCLK_CK_BUFHCLK10 00_21 04_21
    # segbits_int_l.db:207:INT_L.CLK_L0.GCLK_L_B8_WEST !01_21 00_21 00_25 01_20 01_24
    "00_21 00_22 00_26 01_28|00_25 01_20 01_21 01_24",
    "00_23 00_30 01_22 01_25|00_27 00_29 01_26 01_29",
    "01_12 01_14 01_16 01_18|00_10 00_11 01_09 01_10",
    "00_13 01_17 00_15 00_17|00_18 00_19 01_13 00_14",
    "00_34 00_38 01_33 01_37|00_35 00_39 01_38 01_40",
    "00_33 00_41 01_32 01_34|00_37 00_42 01_36 01_41",

    # CLBL?_?.SLICE?_X?.?FF.DMUX
    # ex: segbits_clbll_l.db:8:CLBLL_L.SLICEL_X0.AFF.DMUX.AX !30_00 !30_02 !30_03 30_01
    "30_00 30_01 30_02 30_03",
    "30_24 30_25 30_26 30_27",
    "30_35 30_36 30_37 30_38",
    "30_59 30_60 30_61 30_62",
    "30_04 31_00 31_01 31_02",
    "31_24 31_25 31_26 31_27",
    "31_35 31_36 31_37 31_38",
    "30_58 31_60 31_61 31_62",

    # CLBL?_?.SLICE?_X?.?MUX
    # ex: segbits_clbll_l.db:89:CLBLL_L.SLICEL_X0.AMUX.A5Q !30_06 !30_08 !30_11 30_07
    "30_06 30_07 30_08 30_11",
    "30_20 30_21 30_22 30_23",
    "30_40 30_43 30_44 30_45",
    "30_51 30_52 30_56 30_57",
    "30_05 31_07 31_09 31_10",
    "30_28 30_29 31_20 31_21",
    "30_41 30_42 31_40 31_43",
    "30_53 31_53 31_56 31_57",
]


def parse_line(line):
    parts = line.split()
    # Ex: CLBLL_L.SLICEL_X0.AMUX.A5Q
    tag = parts[0]
    # Ex: !30_06 !30_08 !30_11 30_07
    bits = set(parts[1:])
    return tag, bits


def zero_range(bits, wordmin, wordmax):
    """
    If any bits occur wordmin <= word <= wordmax,
    default bits in wordmin <= word <= wordmax to 0 
    """

    # The bit index, if any, that needs to be one hotted
    bitidx = None
    for bit in bits:
        if bit[0] == "!":
            continue
        fidx, bidx = [int(s) for s in bit.split("_")]
        if wordmin <= fidx <= wordmax:
            assert bitidx is None or bidx == bitidx
            bitidx = bidx

    if bitidx is None:
        return

    for fidx in range(wordmin, wordmax + 1):
        bit = "%02d_%02d" % (fidx, bitidx)
        # Preserve 1 bits, set others to 0
        if bit not in bits:
            bits.add("!" + bit)


def zero_groups(bits, zero_db):
    """
    See if a line occurs within a bit group
    If it does, add 0 bits

    Ex: 01_02 04_05
    Means find a line that has either of these bits
    If either of them occurs, default bits in that set to zero

    Ex: 01_02 04_05 | 07_08 10_11
    If any bits from the first group occur,
    default bits in the second group to zero
    """
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


def add_zero_bits(db_root, tile_type, zero_db):
    '''
    Add multibit entries
    This requires adding some zero bits (ex: !31_09)
    If an entry has any of the
    '''
    dbfile = "%s/segbits_%s.db" % (db_root, tile_type)
    new_lines = set()
    changes = 0

    if not os.path.exists(dbfile):
        return None

    llast = None
    with open(dbfile, "r") as f:
        for line in f:
            # Hack: skip duplicate lines
            # This happens while merging a new multibit entry
            line = line.strip()
            if line == llast:
                continue

            tag, bits = parse_line(line)
            """
            This appears to be a large range of one hot interconnect bits
            They are immediately before the first CLB real bits
            """
            zero_range(bits, 22, 25)
            zero_groups(bits, zero_db)

            new_line = " ".join([tag] + sorted(bits))
            if new_line != line:
                changes += 1
            new_lines.add(new_line)
            llast = line

    with open(dbfile, "w") as f:
        for line in sorted(new_lines):
            print(line, file=f)

    return changes


def update_mask(db_root, mask_db, src_dbs, offset=0):
    bits = set()
    mask_db_file = "%s/mask_%s.db" % (db_root, mask_db)

    if os.path.exists(mask_db_file):
        with open(mask_db_file, "r") as f:
            for line in f:
                line = line.split()
                assert len(line) == 2
                assert line[0] == "bit"
                bits.add(line[1])

    for src_db in src_dbs:
        seg_db_file = "%s/segbits_%s.db" % (db_root, src_db)

        if not os.path.exists(seg_db_file):
            continue

        with open(seg_db_file, "r") as f:
            for line in f:
                line = line.split()
                for bit in line[1:]:
                    if bit[0] == "!":
                        continue
                    if offset != 0:
                        m = re.match(r"(\d+)_(\d+)", bit)
                        bit = "%02d_%02d" % (
                            int(m.group(1)), int(m.group(2)) + offset)
                    bits.add(bit)

    if len(bits) > 0:
        with open(mask_db_file, "w") as f:
            for bit in sorted(bits):
                print("bit %s" % bit, file=f)


def run(
        db_root,
        clb_int=False,
        zero_db_fn=None,
        zero_tile_types=None,
        verbose=False):
    if clb_int:
        zero_db = clb_int_zero_db
        zero_tile_types = [
            "int_l", "int_r", "clbll_l", "clbll_r", "clblm_l", "clblm_r"
        ]
    else:
        assert zero_db_fn
        assert zero_tile_types
        zero_db = open(zero_db_fn, "r").read().split("\n")
    print("CLB INT mode: %s" % clb_int)
    print("Segbit groups: %s" % len(zero_db))

    seg_files = 0
    seg_lines = 0
    for tile_type in zero_tile_types:
        changes = add_zero_bits(db_root, tile_type, zero_db)
        if changes is not None:
            seg_files += 1
            seg_lines += changes
    print(
        "Segbit: checked %u files w/ %u changed lines" %
        (seg_files, seg_lines))

    if clb_int:
        for mask_db, src_dbs in [
            ("clbll_l", ("clbll_l", "int_l")),
            ("clbll_r", ("clbll_r", "int_r")),
            ("clblm_l", ("clblm_l", "int_l")),
            ("clblm_r", ("clblm_r", "int_r")),
            ("hclk_l", ("hclk_l", )),
            ("hclk_r", ("hclk_r", )),
            ("bram_l", ("bram_l", )),
            ("bram_r", ("bram_r", )),
            ("dsp_l", ("dsp_l", )),
            ("dsp_r", ("dsp_r", )),
        ]:
            update_mask(db_root, mask_db, src_dbs)

        for mask_db, src_dbs in [
            ("bram_l", ("int_l", )),
            ("bram_r", ("int_r", )),
            ("dsp_l", ("int_l", )),
            ("dsp_r", ("int_r", )),
        ]:
            for k in range(5):
                update_mask(db_root, mask_db, src_dbs, offset=64 * k)

        print("Mask: checked files")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Create multi-bit entries')

    util.db_root_arg(parser)
    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument(
        '--clb-int', action='store_true', help='Fixup CLB interconnect')
    parser.add_argument('--zero-db', help='Apply custom patches')
    parser.add_argument('--zero-tile_types', help='')
    args = parser.parse_args()

    # XXX: can auto detect this?
    zero_tile_types = args.zero_tile_types.split(
    ) if args.zero_tile_types else None

    run(
        args.db_root, args.clb_int, args.zero_db, zero_tile_types,
        args.verbose)


if __name__ == '__main__':
    main()
