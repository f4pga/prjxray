#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
from prjxray import segmaker

segmk = Segmaker("design.bits")

print("Loading tags")
'''
port,site,tile,pin,val
di[0],IOB_X0Y107,LIOB33_X0Y107,A21,PULLDOWN
di[10],IOB_X0Y147,LIOB33_X0Y147,F14,PULLUP
'''
f = open('design.csv', 'r')
f.readline()
for l in f:
    l = l.strip()
    port, site, tile, pin, val = l.split(',')
    '''
    PULLTYPE    28  29  30
    NONE                X
    KEEPER      X       X
    PULLDOWN
    PULLUP          X   X
    '''
    if val == "":
        val = "NONE"
    segmaker.add_site_group_zero(
        segmk, site, "PULLTYPE.", ("NONE", "KEEPER", "PULLDOWN", "PULLUP"),
        "PULLDOWN", val)

segmk.compile()
segmk.write()
