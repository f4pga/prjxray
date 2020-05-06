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

import subprocess
import demo_sw_led_fasm
import os


def run(roi_dir, swn, ledn):
    design_txt_fn = roi_dir + '/design.txt'
    bit_ref_fn = roi_dir + '/design.bit'
    fasm_fn = 'demo_sw_led.fasm'
    bit_out_fn = 'demo_sw_led.bit'
    ocd_cfg = os.getenv(
        'XRAY_DIR') + '/utils/openocd/board-digilent-basys3.cfg'

    # Clean up old tmp files to be sure we are generating them fresh
    subprocess.call('rm -f %s %s' % (fasm_fn, bit_out_fn), shell=True)

    # subprocess.shell("python3 demo_sw_led.py out_xc7a35tcpg236-1_BASYS3-SWBUT_roi_basev/design.txt 0 0 demo.fasm")
    demo_sw_led_fasm.run(
        open(design_txt_fn, 'r'), swn, ledn, open(fasm_fn, 'w'))
    subprocess.check_call(
        "./fasm2bit.sh %s %s %s" % (fasm_fn, bit_ref_fn, bit_out_fn),
        shell=True)
    subprocess.check_call(
        'openocd -f %s -c "init; pld load 0 %s; exit"' % (ocd_cfg, bit_out_fn),
        shell=True)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Basys3 switch to LED interconnect demo. Compiles and programs')
    parser.add_argument(
        'roi_dir', help='ROI project dir for harness .bit and  metadata.txt')
    parser.add_argument('sw', type=int, help='Switch to use')
    parser.add_argument('led', type=int, help='LED to use')

    args = parser.parse_args()
    run(args.roi_dir, args.sw, args.led)
