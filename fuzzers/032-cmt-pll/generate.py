#!/usr/bin/env python3

import json

from prjxray.segmaker import Segmaker
from prjxray import verilog


def bitfilter(frame, word):
    if frame == 25 and word == 3121:
        return False

    return True


def bus_tags(segmk, ps, site):
    for k in ps:
        segmk.add_site_tag(site, 'param_' + k + '_' + str(ps[k]), 1)

    segmk.add_site_tag(site, 'DWE_CONNECTED', 
            ps['dwe_conn'].startswith('dwe_') or ps['dwe_conn'].startswith('den_'))

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
            segmk.add_site_tag(
                site, 'BANDWIDTH.' + opt,
                1)
        elif verilog.unquote(ps['BANDWIDTH']) == 'LOW':
            segmk.add_site_tag(
                site, 'BANDWIDTH.' + opt,
                0)

    for opt in ['ZHOLD', 'BUF_IN', 'EXTERNAL', 'INTERNAL']:
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

        match = "TRUE" == verilog.unquote(ps['STARTUP_WAIT']) and \
                opt == verilog.unquote(ps['COMPENSATION'])
        segmk.add_site_tag(site, "STARTUP_WAIT_AND_" + opt,
                match)

    segmk.add_site_tag(
            site, 'COMPENSATION.BUF_IN_OR_EXTERNAL',
            verilog.unquote(ps['COMPENSATION']) in ['BUF_IN', 'EXTERNAL'])

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
