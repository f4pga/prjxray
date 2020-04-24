#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
""" Tool for building zero db file for BUFG pips.
This requires that the rdb files be good enough to identify all the 0 candidate
features, which may take multiple manual iterations.  Manual iterations can
be running like:

make ITER=<N> -j<J> database

And then invoking:
python3 build_zdb.py build/segbits_clk_bufg_bot_r.rdb build/segbits_clk_bufg_top_r.rdb > bits.dbf

will successed if and only if the rdb is complete enough.

bits.dbf is committed, so this utility should only be needed to document the
process.

"""
import argparse


def main():
    parser = argparse.ArgumentParser("Form ZDB groups for BUFG.")

    parser.add_argument('bot_r')
    parser.add_argument('top_r')

    args = parser.parse_args()

    groups = {}

    with open(args.bot_r) as f:
        for l in f:
            parts = l.strip().split(' ')
            feature = parts[0]
            bits = parts[1:]
            tile_type, dst, src = feature.split('.')

            assert tile_type == "CLK_BUFG"

            if dst not in groups:
                groups[dst] = {}

            groups[dst][src] = bits

    print('# Generated from build_zdb.py')

    for dst in groups:
        if len(groups[dst]) == 1:
            continue

        bits = set()
        zero_feature = None
        for src in groups[dst]:
            if groups[dst][src][0] == '<0':
                assert zero_feature is None
                zero_feature = src
            else:
                bits |= set(groups[dst][src])

        assert zero_feature is not None, dst

        print(
            '{bits},{type}.{dst}.{src}'.format(
                bits=' '.join(sorted(bits)),
                type='CLK_BUFG',
                dst=dst,
                src=zero_feature))


if __name__ == "__main__":
    main()
