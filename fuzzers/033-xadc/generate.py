#!/usr/bin/env python3

import json

from prjxray.segmaker import Segmaker
from prjxray import verilog


def bus_tags(segmk, ps, site):
    for param in ['INIT_43']:
        paramadj = int(ps[param])
        bitstr = [int(x) for x in "{0:016b}".format(paramadj)[::-1]]
        for i in range(len(bitstr)):
            segmk.add_site_tag(site, '%s[%u]' % (param, i), bitstr[i])


def run():

    segmk = Segmaker("design.bits")

    print("Loading tags")
    f = open('params.jl', 'r')
    f.readline()
    for l in f:
        j = json.loads(l)
        ps = j['params']
        assert j['module'] == 'my_XADC'
        site = verilog.unquote(ps['LOC'])

        bus_tags(segmk, ps, site)

    segmk.compile()
    segmk.write()


run()
