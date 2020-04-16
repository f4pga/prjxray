#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

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

    # rewrite name of AX source net: It's actually AX, BX, CX, or DX
    if src == "AX":
        src = which + "X"

    # add the 1-tag for this connection
    tag = "%sFFMUX.%s" % (which, src)
    segmk.add_site_tag(loc, tag, 1)

    # remove this MUX from the cache, preventing generation of 0-tags for this MUX
    cache[loc].remove(which)

# create 0-tags for all sources on the remaining (unused) MUXes
for loc, muxes in cache.items():
    for which in muxes:
        for src in "F7 F8 CY O5 AX XOR O6 MC31".split():
            if src == "MC31" and which is not "D": continue
            if src == "F7" and which not in "AC": continue
            if src == "F8" and which not in "B": continue
            if src == "AX": src = which + "X"
            tag = "%sFFMUX.%s" % (which, src)
            segmk.add_site_tag(loc, tag, 0)


def bitfilter(frame_idx, bit_idx):

    # Since the SRL32 is enabled along with DFFMUX.MC31, bits related to
    # SRL32 features are masked out.
    if (frame_idx, bit_idx) in [
        (30, 16),  # ALUT.SRL
        (1, 23),  # WEMUX.CE
    ]:
        return False

    return util.bitfilter_clb_mux(frame_idx, bit_idx)


segmk.compile(bitfilter=bitfilter)
segmk.write()
