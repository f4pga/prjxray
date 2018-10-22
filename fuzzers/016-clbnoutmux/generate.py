#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
from prjxray import util

segmk = Segmaker("design.bits")
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
    module, loc, n = l.split(',')
    n = int(n)
    which = chr(ord('A') + n)
    # clb_NFFMUX_AX => AX
    src = module.replace('clb_NOUTMUX_', '')
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

    # if location not included in cache yet: start with assuming all four MUXes are unused.
    if loc not in cache:
        cache[loc] = set("ABCD")

    # rewrite name of F78 source net: MUXes A and C have an F7 input, MUX B has an F8 input
    if src == "F78":
        if which in "AC":
            src = "F7"
        elif which == "B":
            src = "F8"
        else:
            assert 0

    # rewrite name of B5Q source net: It's actually A5Q, B5Q, C5Q, or D5Q
    if src == "B5Q":
        src = which + "5Q"

    # add the 1-tag for this connection
    tag = "%sOUTMUX.%s" % (which, src)
    segmk.add_site_tag(loc, tag, 1)

    # remove this MUX from the cache, preventing generation of 0-tags for this MUX
    cache[loc].remove(which)

# create 0-tags for all sources on the remaining (unused) MUXes
for loc, muxes in cache.items():
    for which in muxes:
        for src in "F7 F8 CY O5 XOR O6 5Q".split():
            if src == "F7" and which not in "AC": continue
            if src == "F8" and which not in "B": continue
            if src == "5Q": src = which + "5Q"
            tag = "%sOUTMUX.%s" % (which, src)
            segmk.add_site_tag(loc, tag, 0)


def bitfilter(frame_idx, bit_idx):
    # locations of A5MA, B5MA, C5MA, D5MA bits. because of the way we generate specimens
    # in this fuzzer we get some aliasing with those bits, so we have to manually exclude
    # them. (Maybe FIXME: read the bit locations from the database files)
    if (frame_idx, bit_idx) in [
        (30, 55),
        (31, 55),  # D5MA
        (31, 44),
        (31, 45),  # C5MA
        (30, 19),
        (31, 19),  # B5MA
        (30, 9),
        (31, 8),  # A5MA
    ]:
        return False

    return util.bitfilter_clb_mux(frame_idx, bit_idx)


segmk.compile(bitfilter=bitfilter)
segmk.write()
