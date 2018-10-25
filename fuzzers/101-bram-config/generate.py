#!/usr/bin/env python3

import json

from prjxray.segmaker import Segmaker
from prjxray import verilog

segmk = Segmaker("design.bits", verbose=True)
#segmk.set_def_bt('BLOCK_RAM')

print("Loading tags")
f = open('params.jl', 'r')
f.readline()
for l in f:
    j = json.loads(l)
    ps = j['params']
    assert j['module'] == 'my_RAMB18E1'
    site = verilog.unquote(ps['LOC'])
    #print('site', site)

    # all of these bits are inverted
    ks = [
        ('IS_CLKARDCLK_INVERTED', 'ZINV_CLKARDCLK'),
        ('IS_CLKBWRCLK_INVERTED', 'ZINV_CLKBWRCLK'),
        ('IS_ENARDEN_INVERTED', 'ZINV_ENARDEN'),
        ('IS_ENBWREN_INVERTED', 'ZINV_ENBWREN'),
        ('IS_RSTRAMARSTRAM_INVERTED', 'ZINV_RSTRAMARSTRAM'),
        ('IS_RSTRAMB_INVERTED', 'ZINV_RSTRAMB'),
        ('IS_RSTREGARSTREG_INVERTED', 'ZINV_RSTREGARSTREG'),
        ('IS_RSTREGB_INVERTED', 'ZINV_RSTREGB'),
    ]
    for param, tagname in ks:
        segmk.add_site_tag(site, tagname, 1 ^ verilog.parsei(ps[param]))
    '''
    parameter DOA_REG = 1'b0;
    parameter DOB_REG = 1'b0;
    parameter SRVAL_A = 18'b0;
    parameter SRVAL_B = 18'b0;
    parameter INIT_A = 18'b0;
    parameter INIT_B = 18'b0;
    '''
    for param, tagname in [('SRVAL_A', 'ZSRVAL_A'), ('SRVAL_B', 'ZSRVAL_B'),
                           ('INIT_A', 'ZINIT_A'), ('INIT_B', 'ZINIT_B')]:
        bitstr = verilog.parse_bitstr(ps[param])
        for i in range(18):
            segmk.add_site_tag(site, '%s[%u]' % (param, i), 1 ^ bitstr[i])

segmk.compile()
segmk.write()
