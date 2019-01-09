#!/usr/bin/env python3

import json
from prjxray import bitstream


def gen_addrs():
    for block_type, top_bottom, cfg_row, cfg_col, frame_count in bitstream.gen_part_base_addrs(
    ):
        yield bitstream.addr_bits2word(
            block_type, top_bottom, cfg_row, cfg_col, 0), frame_count


def run(verbose=False):
    for addr, frame_count in sorted(gen_addrs()):
        print("0x%08X: %u" % (addr, frame_count))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Print number of frames at a base address')
    args = parser.parse_args()

    run(verbose=False)


if __name__ == '__main__':
    main()
