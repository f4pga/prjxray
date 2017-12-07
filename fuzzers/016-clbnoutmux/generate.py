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
    src,loc,n = l.split(',')
    n = int(n)
    which = chr(ord('A') + n)
    # clb_NFFMUX_AX => AX
    src = src.replace('clb_NOUTMUX_', '')

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

    if loc not in cache:
        cache[loc] = set("ABCD")

    if src == "F78":
        if which in "AC":
            src = "F7"
        elif which == "B":
            src = "F8"
        else:
            assert 0

    if src == "B5Q":
        src = which + "5Q"

    tag = "%sMUX.%s" % (which, src)
    segmk.addtag(loc, tag, 1)
    cache[loc].remove(which)

for loc, muxes in cache.items():
    for which in muxes:
        for src in "F7 F8 CY O5 XOR O6 5Q".split():
            if src == "F7" and which not in "AC": continue
            if src == "F8" and which not in "B": continue
            if src == "5Q": src = which + "5Q"
            tag = "%sMUX.%s" % (which, src)
            segmk.addtag(loc, tag, 0)

def bitfilter(frame_idx, bit_idx):
    assert os.getenv("XRAY_DATABASE") == "artix7"

    if (frame_idx, bit_idx) in [
            (30, 55), (31, 55), # D5MA
            (31, 44), (31, 45), # C5MA
            (30, 19), (31, 19), # B5MA
            (30,  9), (31,  8), # A5MA
        ]: return False

    return frame_idx in [30, 31]

segmk.compile(bitfilter=bitfilter)
segmk.write()

