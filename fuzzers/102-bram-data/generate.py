#!/usr/bin/env python3

import sys, re, os

from prjxray.segmaker import Segmaker

c2i = {'0': 0, '1': 1}

segmk = Segmaker("design.bits", verbose=True)
segmk.set_def_bt('BLOCK_RAM')

print("Loading tags")
'''
'''
f = open('params.csv', 'r')
f.readline()
for l in f:
    l = l.strip()
    module, loc, pdata, data = l.split(',')

    for i, d in enumerate(pdata):
        # Keep dec convention used on LUT?
        segmk.add_site_tag(loc, "INITP[%04d]" % i, c2i[d])
    for i, d in enumerate(data):
        # Keep dec convention used on LUT?
        segmk.add_site_tag(loc, "INIT[%04d]" % i, c2i[d])

segmk.compile()
segmk.write()
