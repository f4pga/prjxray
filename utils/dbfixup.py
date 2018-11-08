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
]


def parse_line(line):
    parts = line.split()
    # Ex: CLBLL_L.SLICEL_X0.AMUX.A5Q
    tag = parts[0]
    orig_bits = line.replace(tag + " ", "")
    # <0 candidates> etc
    if "<" in orig_bits:
        return tag, set(), orig_bits

    # Ex: !30_06 !30_08 !30_11 30_07
    bits = set(parts[1:])
    return tag, bits, None


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


def bits_str(bits):
    """Convert a set into canonical form"""
    return ' '.join(sorted(list(bits)))


def zero_groups(tag, bits, zero_db, strict=True, verbose=False):
    """
    See if a line occurs within a bit group
    If it does, add 0 bits

    Ex: 01_02 04_05
    Means find a line that has either of these bits
    If either of them occurs, default bits in that set to zero

    Ex: 01_02 04_05|07_08 10_11
    If any bits from the first group occur,
    default bits in the second group to zero

    Ex: 01_02 04_05,ALL_ZERO
    ALL_ZERO is an enum that is part of the group but is all 0
    It must have 0 candidates

    strict: assert that the size of the given group is the size of the given mask
    """
    for zdb in zero_db:
        allzero_tag = None
        if "," in zdb:
            zdb, allzero_tag = zdb.split(",")

        if "|" in zdb:
            a, b = zdb.split("|")
            a = a.split()
            b = b.split()
        else:
            a = zdb.split()
            b = a

        bitmatch = False
        for bit in a:
            if bit in bits:
                bitmatch = True

        if not (bitmatch or allzero_tag == tag):
            continue

        bits_orig = set(bits)
        for bit in b:
            if bit not in bits:
                bits.add("!" + bit)
        verbose and print(
            "Grouped %s: %s => %s" %
            (tag, bits_str(bits_orig), bits_str(bits)))
        if a == b and strict:
            assert len(bits) == len(
                a), "Mask size %u != DB entry size %u: %s" % (
                    len(a), len(bits), bits_str(bits))


def add_zero_bits(fn_in, fn_out, zero_db, clb_int=False, verbose=False):
    '''
    Add multibit entries
    This requires adding some zero bits (ex: !31_09)
    If an entry has any of the
    '''

    new_lines = set()
    changes = 0

    llast = None
    with open(fn_in, "r") as f:
        for line in f:
            # Hack: skip duplicate lines
            # This happens while merging a new multibit entry
            line = line.strip()
            if line == llast:
                continue

            tag, bits, mode = parse_line(line)
            assert mode not in (
                "<const0>", "<const1>"), "Entries must be resolved"
            if mode:
                assert mode == "<0 candidates>"
            """
            This appears to be a large range of one hot interconnect bits
            They are immediately before the first CLB real bits
            """
            if clb_int:
                zero_range(bits, 22, 25)
            zero_groups(
                tag, bits, zero_db, strict=not clb_int, verbose=verbose)

            new_line = " ".join([tag] + sorted(bits))
            if new_line != line:
                changes += 1
            new_lines.add(new_line)
            llast = line

    with open(fn_out, "w") as f:
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


def load_zero_db(fn):
    # Remove comments and convert to list of lines
    ret = []
    for l in open(fn, "r"):
        pos = l.find("#")
        if pos >= 0:
            l = l[0:pos]
        l = l.strip()
        if not l:
            continue
        ret.append(l)
    return ret


def update_seg_fns(fn_inouts, zero_db, clb_int, lazy=False, verbose=False):
    seg_files = 0
    seg_lines = 0
    for fn_in, fn_out in fn_inouts:
        verbose and print("zb %s: %s" % (fn_in, os.path.exists(fn_in)))
        if lazy and not os.path.exists(fn_in):
            continue

        changes = add_zero_bits(
            fn_in, fn_out, zero_db, clb_int=clb_int, verbose=verbose)
        if changes is not None:
            seg_files += 1
            seg_lines += changes
    print(
        "Segbit: checked %u files w/ %u changed lines" %
        (seg_files, seg_lines))


def update_masks(db_root):
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


def update_segs(
        db_root, clb_int, seg_fn_in, seg_fn_out, zero_db_fn, verbose=False):
    if clb_int:
        zero_db = clb_int_zero_db
        lazy = True

        def gen_fns():
            for tile_type in ["int_l", "int_r", "clbll_l", "clbll_r",
                              "clblm_l", "clblm_r"]:
                fn = "%s/segbits_%s.db" % (db_root, tile_type)
                yield (fn, fn)

        fn_inouts = list(gen_fns())
    else:
        assert seg_fn_in
        assert zero_db_fn
        lazy = False

        if not seg_fn_out:
            seg_fn_out = seg_fn_in

        fn_inouts = [(seg_fn_in, seg_fn_out)]
        zero_db = load_zero_db(zero_db_fn)
    print("CLB INT mode: %s" % clb_int)
    print("Segbit groups: %s" % len(zero_db))
    update_seg_fns(fn_inouts, zero_db, clb_int, lazy=lazy, verbose=verbose)


def run(
        db_root,
        clb_int=False,
        zero_db_fn=None,
        seg_fn_in=None,
        seg_fn_out=None,
        verbose=False):

    # Probably should split this into two programs
    update_segs(
        db_root,
        clb_int=clb_int,
        seg_fn_in=seg_fn_in,
        seg_fn_out=seg_fn_out,
        zero_db_fn=zero_db_fn,
        verbose=verbose)
    if clb_int:
        update_masks()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Create multi-bit entries')

    util.db_root_arg(parser)
    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument(
        '--clb-int', action='store_true', help='Fixup CLB interconnect')
    parser.add_argument('--zero-db', help='Apply custom patches')
    parser.add_argument('--seg-fn-in', help='')
    parser.add_argument('--seg-fn-out', help='')
    args = parser.parse_args()

    run(
        args.db_root, args.clb_int, args.zero_db, args.seg_fn_in,
        args.seg_fn_out, args.verbose)


if __name__ == '__main__':
    main()
