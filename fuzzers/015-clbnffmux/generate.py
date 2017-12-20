#!/usr/bin/env python3

import sys, os, re

sys.path.append("../../../utils/")
from segmaker import segmaker

segmk = segmaker("design.bits")
cache = dict()

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
    src = module.replace('clb_NFFMUX_', '')

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

    if loc not in cache:
        cache[loc] = set("ABCD")

    if src == "F78":
        if which in "AC":
            src = "F7"
        elif which == "B":
            src = "F8"
        else:
            assert 0

    if src == "AX":
        src = which + "X"

    tag = "%sFF.DMUX.%s" % (which, src)
    segmk.addtag(loc, tag, 1)
    cache[loc].remove(which)

for loc, muxes in cache.items():
    for which in muxes:
        for src in "F7 F8 CY O5 AX XOR O6".split():
            if src == "F7" and which not in "AC": continue
            if src == "F8" and which not in "B": continue
            if src == "AX": src = which + "X"
            tag = "%sFF.DMUX.%s" % (which, src)
            segmk.addtag(loc, tag, 0)

def bitfilter(frame_idx, bit_idx):
    assert os.getenv("XRAY_DATABASE") == "artix7"
    return frame_idx in [30, 31]

segmk.compile(bitfilter=bitfilter)
segmk.write()

