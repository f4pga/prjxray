#!/usr/bin/env python3

import os
from prjxray import util


def run(fn_ins, fn_out, strict=False, verbose=False):
    # tag to bits
    entries = {}
    # tag to (bits, line)
    tags = dict()
    # bits to (tag, line)
    bitss = dict()

    for fn_in in fn_ins:
        for line, (tag, bits, mode) in util.parse_db_lines(fn_in):
            line = line.strip()
            assert mode is not None or mode != "always", "strict: got ill defined line: %s" % (
                line, )

            if tag in tags:
                orig_bits, orig_line = tags[tag]
                if orig_bits != bits:
                    print("WARNING: got duplicate tag %s" % (tag, ))
                    print("  Orig line: %s" % orig_line)
                    print("  New line : %s" % line)
                    assert not strict, "strict: got duplicate tag"
            if bits in bitss:
                orig_tag, orig_line = bitss[bits]
                if orig_tag != tag:
                    print("WARNING: got duplicate bits %s" % (bits, ))
                    print("  Orig line: %s" % orig_line)
                    print("  New line : %s" % line)
                    assert not strict, "strict: got duplicate bits"

            entries[tag] = bits
            tags[tag] = (bits, line)
            if bits != None:
                bitss[bits] = (tag, line)

    util.write_db_lines(fn_out, entries)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Combine multiple .db files")

    util.db_root_arg(parser)
    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--out', help='')
    parser.add_argument('ins', nargs='+', help='Last takes precedence')
    args = parser.parse_args()

    run(
        args.ins,
        args.out,
        strict=int(os.getenv("MERGEDB_STRICT", "1")),
        verbose=args.verbose)


if __name__ == '__main__':
    main()
