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

from prjxray.segmaker import Segmaker, add_site_group_zero
from prjxray.verilog import to_int
from prjxray.verilog import quote
import json


def add(segmk, site, dsp, tag, bit, value, invert, is_vector=True):
    tag = "%s.%s%s%s" % (
        dsp, ('Z' if invert else ''), tag, '[%u]' % bit if is_vector else '')
    value = (~value if invert else value)
    value >>= bit
    return segmk.add_site_tag(site, tag, value & 1)


def run():
    segmk = Segmaker("design.bits", verbose=True)

    print("Loading tags")
    with open('params.json', 'r') as fp:
        data = json.load(fp)

    used_dsps = set()

    for params in data['instances']:
        dsp = "DSP_0" if params['SITE'][-1] in "02468" else "DSP_1"
        site = params['SITE']

        if params['USE_DPORT'] == quote(
                "TRUE") and params['USE_MULT'] != quote("NONE"):
            add(segmk, site, dsp, 'ADREG', 0, to_int(params['ADREG']), 1)
        add(segmk, site, dsp, 'ALUMODEREG', 0, to_int(params['ALUMODEREG']), 1)

        if params['A_INPUT'] == quote("DIRECT"):
            add(
                segmk, site, dsp, 'AREG_0', 0,
                int(to_int(params['AREG']) == 0), 0, False)
            add(
                segmk, site, dsp, 'AREG_2', 0,
                int(to_int(params['AREG']) == 2), 0, False)

        if params['B_INPUT'] == quote("DIRECT"):
            add(
                segmk, site, dsp, 'BREG_0', 0,
                int(to_int(params['BREG']) == 0), 0, False)
            add(
                segmk, site, dsp, 'BREG_2', 0,
                int(to_int(params['BREG']) == 2), 0, False)

        if params['A_INPUT'] == quote("CASCADE"):
            add(
                segmk, site, dsp, 'AREG_2_ACASCREG_1', 0,
                int(
                    to_int(params['AREG']) == 2
                    and to_int(params['ACASCREG']) == 1), 0, False)
            add(
                segmk, site, dsp, 'AREG_2_ACASCREG_1', 0,
                int(
                    to_int(params['AREG']) == 2
                    and to_int(params['ACASCREG']) == 1), 1, False)

        if params['B_INPUT'] == quote("CASCADE"):
            add(
                segmk, site, dsp, 'BREG_2_BCASCREG_1', 0,
                int(
                    to_int(params['BREG']) == 2
                    and to_int(params['BCASCREG']) == 1), 0, False)
            add(
                segmk, site, dsp, 'BREG_2_BCASCREG_1', 0,
                int(
                    to_int(params['BREG']) == 2
                    and to_int(params['BCASCREG']) == 1), 1, False)

        add(segmk, site, dsp, 'CARRYINREG', 0, to_int(params['CARRYINREG']), 1)
        add(
            segmk, site, dsp, 'CARRYINSELREG', 0,
            to_int(params['CARRYINSELREG']), 1)
        add(segmk, site, dsp, 'CREG', 0, to_int(params['CREG']), 1)
        if params['USE_DPORT'] == quote(
                "TRUE") and params['USE_MULT'] != quote("NONE"):
            add(segmk, site, dsp, 'DREG', 0, to_int(params['DREG']), 1)
        add(segmk, site, dsp, 'INMODEREG', 0, to_int(params['INMODEREG']), 1)
        add(segmk, site, dsp, 'OPMODEREG', 0, to_int(params['OPMODEREG']), 1)
        add(segmk, site, dsp, 'PREG', 0, to_int(params['PREG']), 1)

        INPUT = {}
        INPUT[quote('DIRECT')] = 0
        INPUT[quote('CASCADE')] = 1

        add(segmk, site, dsp, 'A_INPUT', 0, INPUT[params['A_INPUT']], 0)
        add(segmk, site, dsp, 'B_INPUT', 0, INPUT[params['B_INPUT']], 0)

        BOOL = {}
        BOOL[quote('FALSE')] = 0
        BOOL[quote('TRUE')] = 1

        add(segmk, site, dsp, 'USE_DPORT', 0, BOOL[params['USE_DPORT']], 0)

        add(
            segmk, site, dsp, 'USE_SIMD_FOUR12', 0,
            params['USE_SIMD'] == quote("FOUR12"), 0, False)
        add(
            segmk, site, dsp, 'USE_SIMD_FOUR12_TWO24', 0,
            params['USE_SIMD'] in (quote("TWO24"), quote("FOUR12")), 0, False)

        MULT = {}
        MULT[quote('NONE')] = 0
        MULT[quote('MULTIPLY')] = 1
        MULT[quote('DYNAMIC')] = 2

        for i in range(2):
            add(segmk, site, dsp, 'USE_MULT', i, MULT[params['USE_MULT']], 0)

        add(segmk, site, dsp, 'MREG', 0, to_int(params['MREG']), 1)

        AUTORESET = {}
        AUTORESET[quote('NO_RESET')] = 0
        AUTORESET[quote('RESET_NOT_MATCH')] = 1
        AUTORESET[quote('RESET_MATCH')] = 2

        add(
            segmk, site, dsp, 'AUTORESET_PATDET_RESET_NOT_MATCH', 0,
            params['AUTORESET_PATDET'] == quote("RESET_NOT_MATCH"), 0, False)
        add(
            segmk, site, dsp, 'AUTORESET_PATDET_RESET', 0,
            params['AUTORESET_PATDET'] in (
                quote("RESET_NOT_MATCH"), quote("RESET_MATCH")), 0, False)

        for i in range(48):
            add(segmk, site, dsp, 'MASK', i, to_int(params['MASK']), 0)

        for i in range(48):
            add(segmk, site, dsp, 'PATTERN', i, to_int(params['PATTERN']), 0)

        if params['USE_PATTERN_DETECT'] == quote("PATDET"):
            add_site_group_zero(
                segmk, site, dsp + ".", [
                    "SEL_MASK_%s" % x
                    for x in ["MASK", "C", "ROUNDING_MODE1", "ROUNDING_MODE2"]
                ], "SEL_MASK_MASK", "SEL_MASK_%s" % (params['SEL_MASK'][1:-1]))

        USE_PATTERN_DETECT = {}
        USE_PATTERN_DETECT[quote('NO_PATDET')] = 0
        USE_PATTERN_DETECT[quote('PATDET')] = 1

        add(
            segmk, site, dsp, 'USE_PATTERN_DETECT', 0,
            USE_PATTERN_DETECT[params['USE_PATTERN_DETECT']], 0)

        inv_ports = [
            ("ALUMODE", 4),
            ("CARRYIN", 1),
            ("CLK", 1),
            ("INMODE", 5),
            ("OPMODE", 7),
        ]

        for port, width in inv_ports:
            param = 'IS_{}_INVERTED'.format(port)
            for i in range(width):
                add(
                    segmk, site, dsp, param, i, to_int(params[param]), 1,
                    width > 1)

    segmk.compile()
    segmk.write()


if __name__ == '__main__':
    run()
