#!/usr/bin/env python3

import json

from prjxray.segmaker import Segmaker
from prjxray import verilog


def bus_tags(segmk, ps, site):
    for param, tagname in [('CLKOUT0_DIVIDE', 'ZCLKOUT0_DIVIDE')]:
        # 1-128 => 0-127 for actual 7 bit value
        paramadj = int(ps[param]) - 1
        bitstr = [int(x) for x in "{0:07b}".format(paramadj)[::-1]]
        # FIXME: only bits 0 and 1 resolving
        # for i in range(7):
        for i in range(2):
            segmk.add_site_tag(site, '%s[%u]' % (param, i), 1 ^ bitstr[i])


def run():

    segmk = Segmaker("design.bits")

    print("Loading tags")
    f = open('params.jl', 'r')
    f.readline()
    for l in f:
        j = json.loads(l)
        ps = j['params']
        assert j['module'] == 'my_PLLE2_ADV'
        site = verilog.unquote(ps['LOC'])

        bus_tags(segmk, ps, site)

    segmk.compile()
    segmk.write()


run()
