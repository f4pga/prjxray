#!/usr/bin/env python3

import sys, re

from prjxray.segmaker import Segmaker

segmk = Segmaker("design.bits")

print("Loading tags")
'''
name,loc,ce,r
clb_FDRE,SLICE_X12Y100,1,0
clb_FDRE,SLICE_X13Y100,1,1
clb_FDRE,SLICE_X14Y100,1,1
'''
f = open('params.csv', 'r')
f.readline()
for l in f:
    name, site, ce, r = l.split(',')
    ce = int(ce)
    r = int(r)

    # Theory: default position are the force positions
    # parameter FORCE_CE1=0;
    # parameter nFORCE_R0=1;
    # .CE(din[0] | FORCE_CE1),
    # .R(din[1] & nFORCE_R0),
    segmk.addtag(site, "CEUSEDMUX", ce ^ 1)
    segmk.addtag(site, "SRUSEDMUX", r)
segmk.compile()
segmk.write()
