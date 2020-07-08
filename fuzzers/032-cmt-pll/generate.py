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


def bus_tags(segmk, ps, site):
    segmk.add_site_tag(site, 'IN_USE', ps['active'])

    if not ps['active']:
        return

    for k in ps:
        segmk.add_site_tag(site, 'param_' + k + '_' + str(ps[k]), 1)

    for reg, invert in [
        ('RST', 1),
        ('PWRDWN', 1),
        ('CLKINSEL', 0),
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

    for opt in ['ZHOLD', 'BUF_IN', 'EXTERNAL', 'INTERNAL']:
        continue

        opt_match = verilog.unquote(ps['COMPENSATION']) == opt

        if ps['clkfbin_conn'] == '':
            segmk.add_site_tag(site, 'COMP.NOFB_' + opt, opt_match)
            segmk.add_site_tag(site, 'COMP.ZNOFB_' + opt, opt_match)
            continue

        for conn in ['clk', 'clkfbout_mult_BUFG_' + ps['site'],
                     'clkfbout_mult_' + ps['site']]:
            conn_match = ps['clkfbin_conn'] == conn
            segmk.add_site_tag(
                site, 'COMP.' + opt + '_' + conn + '_' + ps['site'], opt_match
                and conn_match)
            segmk.add_site_tag(
                site, 'COMP.Z' + opt + '_' + conn + '_' + ps['site'],
                not opt_match and conn_match)
            segmk.add_site_tag(
                site, 'COMP.Z' + opt + '_Z' + conn + '_' + ps['site'],
                not opt_match and not conn_match)
            segmk.add_site_tag(
                site, 'COMP.' + opt + '_Z' + conn + '_' + ps['site'], opt_match
                and not conn_match)

    bufg_on_clkin = \
            'BUFG' in ps['clkin1_conn'] or \
            'BUFG' in ps['clkin2_conn']

    # This one is in conflict with some clock routing bits.
    #    match = verilog.unquote(ps['COMPENSATION']) in ['BUF_IN', 'EXTERNAL']
    #    if not match:
    #        if verilog.unquote(ps['COMPENSATION']) == 'ZHOLD' and bufg_on_clkin:
    #            match = True
    #    segmk.add_site_tag(
    #        site, 'COMPENSATION.BUF_IN_OR_EXTERNAL_OR_ZHOLD_CLKIN_BUF', match)

    match = verilog.unquote(ps['COMPENSATION']) in ['ZHOLD']
    segmk.add_site_tag(
        site, 'COMPENSATION.Z_ZHOLD_OR_CLKIN_BUF', not match
        or (match and bufg_on_clkin))
    segmk.add_site_tag(
            site, 'COMPENSATION.ZHOLD_NO_CLKIN_BUF', match and \
                    not bufg_on_clkin
                    )
    segmk.add_site_tag(
            site, 'COMPENSATION.ZHOLD_NO_CLKIN_BUF_NO_TOP', match and \
                    not bufg_on_clkin and \
                    site != "PLLE2_ADV_X0Y3" and site != "PLLE2_ADV_X0Y0"
                    )
    segmk.add_site_tag(
            site, 'COMP.ZHOLD_NO_CLKIN_BUF_TOP', match and \
                    not bufg_on_clkin and \
                    (site == "PLLE2_ADV_X0Y3" or site == "PLLE2_ADV_X0Y0")
                    )

    # No INTERNAL as it has conflicting bits
    for opt in ['ZHOLD', 'BUF_IN', 'EXTERNAL']:
        if opt in ['BUF_IN', 'EXTERNAL']:
            if ps['clkfbin_conn'] not in ['', 'clk']:
                continue

        if site == "PLLE2_ADV_X0Y2" and opt == 'ZHOLD':
            segmk.add_site_tag(
                site, 'TOP.COMPENSATION.' + opt,
                verilog.unquote(ps['COMPENSATION']) == opt)
        else:
            segmk.add_site_tag(
                site, 'COMPENSATION.' + opt,
                verilog.unquote(ps['COMPENSATION']) == opt)
        segmk.add_site_tag(
            site, 'COMPENSATION.Z_' + opt,
            verilog.unquote(ps['COMPENSATION']) != opt)


# This one has bits that are in conflict with clock routing
#    segmk.add_site_tag(
#        site, 'COMPENSATION.INTERNAL',
#        verilog.unquote(ps['COMPENSATION']) in ['INTERNAL'])

    for param in ['CLKFBOUT_MULT']:
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
        ('CLKOUT0_DIVIDE', 7),
        ('CLKOUT1_DIVIDE', 7),
        ('CLKOUT2_DIVIDE', 7),
        ('CLKOUT3_DIVIDE', 7),
        ('CLKOUT4_DIVIDE', 7),
        ('CLKOUT5_DIVIDE', 7),
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

    print("Loading tags")
    f = open('params.jl', 'r')
    f.readline()
    for l in f:
        j = json.loads(l)
        bus_tags(segmk, j, j['site'])

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


run()
