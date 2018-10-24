#!/usr/bin/env python3

import json

from prjxray.segmaker import Segmaker
from prjxray import verilog

segmk = Segmaker("design.bits", verbose=True)

print("Loading tags")
f = open('params.jl', 'r')
f.readline()
for l in f:
    j = json.loads(l)
    ps = j['params']
    assert j['module'] == 'my_RAMB36E1'
    site = verilog.unquote(ps['LOC'])

    ks = [
        'IS_CLKARDCLK_INVERTED',
        'IS_CLKBWRCLK_INVERTED',
        'IS_ENARDEN_INVERTED',
        'IS_ENBWREN_INVERTED',
        'IS_RSTRAMARSTRAM_INVERTED',
        'IS_RSTRAMB_INVERTED',
        'IS_RSTREGARSTREG_INVERTED',
        'IS_RSTREGB_INVERTED',
    ]

    for k in ks:
        segmk.add_site_tag(site, k, verilog.parsei(ps[k]))

segmk.compile()
segmk.write()
