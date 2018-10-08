#!/usr/bin/env python3

import sys, re, os

sys.path.append("../../../utils/")
from segmaker import segmaker

c2i = {'0': 0, '1': 1}

segmk = segmaker("design.bits")

print("Loading tags")
'''
'''
f = open('params.csv', 'r')
f.readline()
for l in f:
    l = l.strip()
    module, loc, pdata, data = l.split(',')
    print(loc)

    segmk.addtag(loc, "STUFF", 1)

    for i, d in enumerate(pdata):
        # Keep dec convention used on LUT?
        segmk.addtag(loc, "BRAM.INITP[%04d]" % i, c2i[d])
    for i, d in enumerate(data):
        # Keep dec convention used on LUT?
        segmk.addtag(loc, "BRAM.INIT[%04d]" % i, c2i[d])

segmk.compile()
segmk.write()
