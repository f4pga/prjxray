#!/usr/bin/env python3

import json

from prjxray.segmaker import Segmaker
from prjxray import verilog


def bus_tags(segmk, ps, site):
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

    for opt in ['ZHOLD', 'BUF_IN', 'EXTERNAL', 'INTERNAL']:
        segmk.add_site_tag(
            site, 'COMPENSATION.' + opt,
            verilog.unquote(ps['COMPENSATION']) == opt)

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

    segmk.compile()
    segmk.write()


run()
