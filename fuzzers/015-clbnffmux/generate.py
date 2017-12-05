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
    module = module.replace('clb_NFFMUX_', '')

    '''
    AFFMUX
            30_00   30_01   30_02   30_03
    F78     1       1
    CY      1               1
    O5      1                       1
    AX              1
    XOR                     1
    O6                              1
    '''
    # TODO: this needs to be converted to PIP type format
    if 0:
        # Although F78 is special, if it doesn't show up, we don't care
        segmk.addtag(loc, "%cFF.DMUX.B0" % which, module in ('F78', 'CY', 'O5'))
        segmk.addtag(loc, "%cFF.DMUX.B1" % which, module in ('F78', 'AX'))
        segmk.addtag(loc, "%cFF.DMUX.B2" % which, module in ('CY', 'XOR'))
        segmk.addtag(loc, "%cFF.DMUX.B3" % which, module in ('O5', 'O6'))

segmk.compile()
segmk.write()

