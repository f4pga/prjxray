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

import json

from prjxray.segmaker import Segmaker
from prjxray import verilog


def bitfilter(frame, word):
    if frame < 28:
        return False

    return True


def bus_tags(segmk, ps, all_params, site):
    segmk.add_site_tag(site, 'IN_USE', ps['active'])

    if not ps['active']:
        return

    params = all_params[site]["params"]

    #for k in ps:
    #    segmk.add_site_tag(site, 'param_' + k + '_' + str(ps[k]), 1)

    for reg, invert in [
        ('RST', 1),
        ('PWRDWN', 1),
        ('CLKINSEL', 0),
        ('PSEN', 1),
        ('PSINCDEC', 1),
    ]:
        opt = 'IS_{}_INVERTED'.format(reg)

        if invert:
            segmk.add_site_tag(site, 'ZINV_' + reg, 1 ^ ps[opt])
        else:
            segmk.add_site_tag(site, 'INV_' + reg, ps[opt])

    for opt in ['OPTIMIZED', 'HIGH', 'LOW']:
        if verilog.unquote(ps['BANDWIDTH']) == opt:
            segmk.add_site_tag(site, 'BANDWIDTH.' + opt, 1)
        elif verilog.unquote(ps['BANDWIDTH']) == 'LOW':
            segmk.add_site_tag(site, 'BANDWIDTH.' + opt, 0)

    # "INTERNAL" compensation conflicts with the CLKFBOUT2IN->CLKFBIN PIP.
    # There is no telling which of these two is actually controlled by those
    # bits. It is better to leave them for the PIP.
    COMPENSATION_OPTS = ['ZHOLD', 'BUF_IN', 'EXTERNAL']

    for opt in COMPENSATION_OPTS:
        val = params["COMPENSATION"] == opt
        segmk.add_site_tag(site, "COMP.{}".format(opt), val)
        segmk.add_site_tag(site, "COMP.Z_{}".format(opt), not val)

    opt = (verilog.unquote(ps["SS_EN"]) == "TRUE")
    segmk.add_site_tag(site, "SS_EN", opt)

    for param in ['CLKFBOUT_MULT_F']:
        paramadj = int(ps[param])
        bitstr = [int(x) for x in "{0:09b}".format(paramadj)[::-1]]
        for i in range(7):
            segmk.add_site_tag(site, '%s[%u]' % (param, i), bitstr[i])

    for param in ['CLKOUT0_DUTY_CYCLE']:
        assert ps[param][:2] == '0.', ps[param]
        assert len(ps[param]) == 5
        paramadj = int(ps[param][2:])
        bitstr = [int(x) for x in "{0:011b}".format(paramadj)[::-1]]

        for i in range(10):
            segmk.add_site_tag(site, '%s[%u]' % (param, i), bitstr[i])

    for param, bits in [
        ('CLKOUT0_DIVIDE_F', 7),
        ('CLKOUT1_DIVIDE', 7),
        ('CLKOUT2_DIVIDE', 7),
        ('CLKOUT3_DIVIDE', 7),
        ('CLKOUT4_DIVIDE', 7),
        ('CLKOUT5_DIVIDE', 7),
        ('CLKOUT6_DIVIDE', 7),
        ('DIVCLK_DIVIDE', 6),
    ]:
        # 1-128 => 0-127 for actual 7 bit value
        paramadj = int(ps[param])
        if paramadj < 4:
            continue

        bitstr = [int(x) for x in "{0:09b}".format(paramadj)[::-1]]
        for i in range(bits):
            segmk.add_site_tag(site, '%s[%u]' % (param, i), bitstr[i])

    segmk.add_site_tag(
        site, 'STARTUP_WAIT',
        verilog.unquote(ps['STARTUP_WAIT']) == 'TRUE')


def run():

    segmk = Segmaker("design.bits")

    print("Loading params")
    f = open("params.json")
    params = json.load(f)
    params = {p["site"]: p for p in params}

    print("Loading tags")
    f = open('params.jl', 'r')
    f.readline()
    for l in f:
        j = json.loads(l)
        bus_tags(segmk, j, params, j['site'])

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


run()
