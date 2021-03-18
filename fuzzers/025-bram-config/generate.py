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
import csv

from prjxray.segmaker import Segmaker
from prjxray import verilog
from prjxray import segmaker


def isinv_tags(segmk, ps, site, actual_ps):
    # all of these bits are inverted
    ks = [
        ('IS_CLKARDCLK_INVERTED', 'ZINV_CLKARDCLK'),
        ('IS_CLKBWRCLK_INVERTED', 'ZINV_CLKBWRCLK'),
        ('IS_REGCLKARDRCLK_INVERTED', 'ZINV_REGCLKARDRCLK'),
        ('IS_REGCLKB_INVERTED', 'ZINV_REGCLKB'),
        ('IS_ENARDEN_INVERTED', 'ZINV_ENARDEN'),
        ('IS_ENBWREN_INVERTED', 'ZINV_ENBWREN'),
        ('IS_RSTRAMARSTRAM_INVERTED', 'ZINV_RSTRAMARSTRAM'),
        ('IS_RSTRAMB_INVERTED', 'ZINV_RSTRAMB'),
        ('IS_RSTREGARSTREG_INVERTED', 'ZINV_RSTREGARSTREG'),
        ('IS_RSTREGB_INVERTED', 'ZINV_RSTREGB'),
    ]

    for param, tagname in ks:
        # The CLK inverts sometimes are changed during synthesis, resulting
        # in addition inversions.  Take this into account.
        if param in actual_ps:
            tag = 1 ^ verilog.parsei(actual_ps[param])
        elif param == 'IS_REGCLKARDRCLK_INVERTED':
            if verilog.parsei(ps['DOA_REG']):
                # When DOA_REG == 1, REGCLKARDRCLK follows the CLKARDCLK setting.
                tag = 1 ^ verilog.parsei(actual_ps['IS_CLKARDCLK_INVERTED'])
            else:
                # When DOA_REG == 0, REGCLKARDRCLK is always inverted.
                tag = 0

            segmk.add_site_tag(site, tagname, tag)
        elif param == 'IS_REGCLKB_INVERTED':
            if verilog.parsei(ps['DOB_REG']):
                # When DOB_REG == 1, REGCLKB follows the CLKBWRCLK setting.
                tag = 1 ^ verilog.parsei(actual_ps['IS_CLKBWRCLK_INVERTED'])
            else:
                # When DOB_REG == 0, REGCLKB is always inverted.
                tag = 0

        else:
            tag = 1 ^ verilog.parsei(ps[param])

        segmk.add_site_tag(site, tagname, tag)


def bus_tags(segmk, ps, site):
    for param in ("DOA_REG", "DOB_REG"):
        segmk.add_site_tag(site, param, verilog.parsei(ps[param]))

    for param, tagname in [('SRVAL_A', 'ZSRVAL_A'), ('SRVAL_B', 'ZSRVAL_B'),
                           ('INIT_A', 'ZINIT_A'), ('INIT_B', 'ZINIT_B')]:
        bitstr = verilog.parse_bitstr(ps[param])
        ab = param[-1]
        # Are all bits present?
        hasparity = ps['READ_WIDTH_' + ab] == 18
        for i in range(18):
            # Magic bit positions from experimentation
            # we could just only solve when parity, but this check documents the fine points a bit better
            if hasparity or i not in (1, 9):
                segmk.add_site_tag(
                    site, '%s[%u]' % (tagname, i), 1 ^ bitstr[i])


def rw_width_tags(segmk, ps, site):
    '''
    Y0.READ_WIDTH_A
    width   001_03  001_04  001_05
    1       0       0       0
    2       1       0       0
    4       0       1       0
    9       1       1       0
    18      0       0       1
    '''
    params = ["READ_WIDTH_A", "READ_WIDTH_B", "WRITE_WIDTH_A", "WRITE_WIDTH_B"]

    for param in params:
        set_val = int(ps[param])

        if set_val == 0:
            set_val = 1

        if set_val >= 36:
            continue

        def mk(x):
            return '%s_%u' % (param, x)

        segmaker.add_site_group_zero(
            segmk, site, "",
            [mk(1), mk(2), mk(4), mk(9), mk(18)], mk(1), mk(set_val))


def write_mode_tags(segmk, ps, site):
    for param in ["WRITE_MODE_A", "WRITE_MODE_B"]:
        set_val = verilog.unquote(ps[param])
        # WRITE_FIRST: no bits set
        segmk.add_site_tag(
            site, '%s_READ_FIRST' % (param), set_val == "READ_FIRST")
        segmk.add_site_tag(
            site, '%s_NO_CHANGE' % (param), set_val == "NO_CHANGE")


def write_rstreg_priority(segmk, ps, site):
    for param in ["RSTREG_PRIORITY_A", "RSTREG_PRIORITY_B"]:
        set_val = verilog.unquote(ps[param])
        for opt in ["RSTREG", "REGCE"]:
            segmk.add_site_tag(
                site, "{}_{}".format(param, opt), set_val == opt)


def write_rdaddr_collision(segmk, ps, site):
    for opt in ["DELAYED_WRITE", "PERFORMANCE"]:
        set_val = verilog.unquote(ps['RDADDR_COLLISION_HWCONFIG'])
        segmk.add_site_tag(
            site, "RDADDR_COLLISION_HWCONFIG_{}".format(opt), set_val == opt)


def run():

    segmk = Segmaker("design.bits")

    clk_inverts = {}
    with open('design.csv', 'r') as f:
        for params in csv.DictReader(f):
            clk_inverts[params['site']] = params

    print("Loading tags")
    f = open('params.jl', 'r')
    f.readline()
    for l in f:
        j = json.loads(l)
        ps = j['params']
        assert j['module'] == 'my_RAMB18E1'
        site = verilog.unquote(ps['LOC'])

        bus_tags(segmk, ps, site)
        if ps['RAM_MODE'] == '"TDP"':
            rw_width_tags(segmk, ps, site)
        segmk.add_site_tag(
            site, 'SDP_READ_WIDTH_36', ps['RAM_MODE'] == '"SDP"'
            and int(ps['READ_WIDTH_A']) == 36)
        segmk.add_site_tag(
            site, 'SDP_WRITE_WIDTH_36', ps['RAM_MODE'] == '"SDP"'
            and int(ps['WRITE_WIDTH_B']) == 36)

        if ps['READ_WIDTH_A'] < 36 and ps['WRITE_WIDTH_B'] < 36:
            isinv_tags(segmk, ps, site, clk_inverts[site])
            write_mode_tags(segmk, ps, site)
            write_rstreg_priority(segmk, ps, site)
            write_rdaddr_collision(segmk, ps, site)

    def bitfilter(frame, bit):
        # rw_width_tags() aliasing interconnect on large widths
        return frame not in (0, 20, 21)

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


run()
