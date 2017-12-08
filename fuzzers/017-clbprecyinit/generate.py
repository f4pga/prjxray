#!/usr/bin/env python3

import sys, os, re

sys.path.append("../../../utils/")
from segmaker import segmaker

segmk = segmaker("design.bits")

print("Loading tags")
f = open('params.csv', 'r')
f.readline()
for l in f:
    module,loc,loc2 = l.split(',')
    # clb_PRECYINIT_AX => AX
    src = module.replace('clb_PRECYINIT_', '')
    print(src, src == '0')
    #if src == 'CIN':
    #    continue

    '''
    PRECYINIT
                00_12   30_14   30_13
    1           0       1       0
    AX          1       0       0
    CIN         0       0       1
    0           0       0       0
    '''
    srcs = ('0', '1', 'AX', 'CIN')
    for asrc in srcs:
        segmk.addtag(loc, "PRECYINIT.%s" % asrc, int(src == asrc))

segmk.compile()
segmk.write()

