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

import sys
import os
sys.path.append(os.getenv("XRAY_UTILS_DIR"))
import simpleroute

print()
print('ready')


def load_design(f):
    '''
    name node pin wire
    clk CLK_HROW_TOP_R_X60Y130/CLK_HROW_CK_BUFHCLK_L0 W5 HCLK_VBRK_X34Y130/HCLK_VBRK_CK_BUFHCLK0
    din[0] INT_R_X9Y100/NE2BEG3 V17 VBRK_X29Y106/VBRK_NE2A3
    '''
    ret = {}
    f.readline()
    for l in f:
        l = l.strip()
        name, node, pin, wire = l.split(' ')
        ret[name] = wire
    return ret


def route2fasm(route, out_f):
    pips = simpleroute.route(route)
    for pip in pips:
        # INT_L_X10Y122.NL1BEG2.NE2END3
        # to
        # INT_L_X10Y122.NL1BEG2 NE2END3
        doti = pip.rfind('.')
        pip = pip[0:doti] + ' ' + pip[doti + 1:]
        out_f.write(pip + '\n')


def run(design_f, swn, ledn, out_f):
    name2wire = load_design(design_f)
    led_name = 'dout[%d]' % ledn
    sw_name = 'din[%d]' % swn
    led_wire = name2wire[led_name]
    sw_wire = name2wire[sw_name]
    print(
        'Routing %s (%s) => %s (%s)' % (sw_wire, sw_name, led_wire, led_name))

    route2fasm((sw_wire, led_wire), out_f)
    # XXX: terminate LEDs so they are off?


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Switch to LED interconnect demo: FASM generator')
    parser.add_argument('design_txt', help='ROI metadata file')
    parser.add_argument('sw', type=int, help='Switch to use')
    parser.add_argument('led', type=int, help='LED to use')
    # For now can't use stdout since simpleroute is spewing out prints
    parser.add_argument('out_fasm', help='Output .fasm file')

    args = parser.parse_args()
    run(
        open(args.design_txt, 'r'), args.sw, args.led, open(
            args.out_fasm, 'w'))
