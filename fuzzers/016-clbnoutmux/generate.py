#!/usr/bin/env python3

import sys, re

sys.path.append("../../../utils/")
from segmaker import segmaker

segmk = segmaker("design.bits")

print("Loading tags")
'''
module,loc,n
clb_NFFMUX_O5,SLICE_X12Y100,3
clb_NFFMUX_AX,SLICE_X13Y100,2
clb_NFFMUX_O6,SLICE_X14Y100,3
'''
f = open('params.csv', 'r')
f.readline()
for l in f:
    module,loc,n = l.split(',')
    n = int(n)
    which = chr(ord('A') + n)
    # clb_NFFMUX_AX => AX
    module = module.replace('clb_NOUTMUX_', '')

    '''
    BOUTMUX
            30_20   30_21    30_22   30_23
    O6      1
    O5      1               1
    XOR             1
    CY              1       1
    F8                      1       1
    B5Q                             1
    '''
    # TODO: this needs to be converted to PIP type format
    if 0:
        # Although F78 is special, if it doesn't show up, we don't care
        segmk.addtag(loc, "%cMUX.B0" % which, module in ('O6', 'O5'))
        segmk.addtag(loc, "%cMUX.B1" % which, module in ('XOR', 'CY'))
        segmk.addtag(loc, "%cMUX.B2" % which, module in ('O5', 'CY', 'F78'))
        segmk.addtag(loc, "%cMUX.B3" % which, module in ('F78', 'B5Q'))

segmk.compile()
segmk.write()

