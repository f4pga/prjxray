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
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Converts generic BRAM pips to BRAM_L and BRAM_R pips.")

    parser.add_argument('--bram_x', required=True)
    parser.add_argument('--bram_l', required=True)
    parser.add_argument('--bram_r', required=True)

    args = parser.parse_args()

    with open(args.bram_x, 'r') as f_in, open(
            args.bram_l, 'w') as f_l_out, open(args.bram_r, 'w') as f_r_out:
        for l in f_in:
            # BRAM_L has the same pip names as BRAM_X
            print(l.strip(), file=f_l_out)

            # BRAM_R has some _R_ added to some pips.
            #
            # BRAM.BRAM_ADDRARDADDRL0.BRAM_IMUX_ADDRARDADDRL0
            #
            # becomes
            #
            # BRAM.BRAM_ADDRARDADDRL0.BRAM_IMUX_R_ADDRARDADDRL0
            print(
                l.strip().replace('BRAM_IMUX_ADDR', 'BRAM_R_IMUX_ADDR'),
                file=f_r_out)


if __name__ == '__main__':
    main()
