#!/usr/bin/env python3

import sys, re

sys.path.append("../../../utils/")
from segmaker import segmaker

segmk = segmaker("design.bits")

print("Loading tags")
'''
module,loc,n,def_a
clb_N5FFMUX,SLICE_X12Y100,3,1
clb_N5FFMUX,SLICE_X13Y100,0,1
clb_N5FFMUX,SLICE_X14Y100,3,1
'''
f = open('params.csv', 'r')
f.readline()
for l in f:
    module, loc, n, def_a = l.split(',')
    def_a = int(def_a)
    n = int(n)
    #which = chr(ord('A') + n)

    for i, which in enumerate('ABCD'):
        # Theory: there is one bit for each mux positon
        # In each config 3 muxes are in one position, other 3 are in another
        inv = int(i == n)
        segmk.addtag(loc, "%c5FF.MUX.A" % which, def_a ^ inv)
        segmk.addtag(loc, "%c5FF.MUX.B" % which, 1 ^ def_a ^ inv)
segmk.compile()
segmk.write()
