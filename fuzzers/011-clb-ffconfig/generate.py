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
'''
FDCE Primitive: D Flip-Flop with Clock Enable and Asynchronous Clear
FDPE Primitive: D Flip-Flop with Clock Enable and Asynchronous Preset
FDRE Primitive: D Flip-Flop with Clock Enable and Synchronous Reset
FDSE Primitive: D Flip-Flop with Clock Enable and Synchronous Set
LDCE Primitive: Transparent Data Latch with Asynchronous Clear and Gate Enable
LDPE Primitive: Transparent Data Latch with Asynchronous Preset and Gate Enable
'''

from prims import *

from prjxray.segmaker import Segmaker

segmk = Segmaker("design.bits")


def ones(l):
    #return l + [x + '_1' for x in l]
    #return sorted(l + [x + '_1' for x in l])
    ret = []
    for x in l:
        ret.append(x)
        ret.append(x + '_1')
    return ret


def loadtop():
    '''
    i,prim,loc,bel
    0,FDPE,SLICE_X12Y100,C5FF
    1,FDPE,SLICE_X15Y100,A5FF
    2,FDPE_1,SLICE_X16Y100,B5FF
    3,LDCE_1,SLICE_X17Y100,BFF
    '''
    f = open('top.txt', 'r')
    f.readline()
    ret = {}
    for l in f:
        i, prim, loc, bel, init = l.split(",")
        i = int(i)
        init = int(init)
        ret[loc] = (i, prim, loc, bel, init)
    return ret


top = loadtop()


def vs2i(s):
    return {"1'b0": 0, "1'b1": 1}[s]


print("Loading tags from design.txt")
with open("design.txt", "r") as f:
    for line in f:
        '''
        puts $fp "$type $tile $grid_x $grid_y $ff $bel_type $used $usedstr"

        CLBLM_L CLBLM_L_X10Y137 30 13 SLICE_X13Y137/AFF REG_INIT 1 FDRE
        CLBLM_L CLBLM_L_X10Y137 30 13 SLICE_X12Y137/D5FF FF_INIT 0
        '''
        line = line.split()
        tile_type = line[0]
        tile_name = line[1]
        grid_x = line[2]
        grid_y = line[3]
        # Other code uses BEL name
        # SLICE_X12Y137/D5FF
        site_ff_name = line[4]
        site, ff_name = site_ff_name.split('/')
        ff_type = line[5]
        used = int(line[6])
        cel_prim = None
        cel_name = None
        if used:
            cel_name = line[7]
            # ex: FDCE
            cel_prim = line[8]
            # 1'b1
            # cinv = int(line[9][-1])
            cinv = int(line[9])
            init = vs2i(line[10])
            #init = int(line[10])

        # A B C D
        which = ff_name[0]
        # LUT6 vs LUT5 FF
        is5 = '5' in ff_name

        if used:
            segmk.add_site_tag(site, "%s.ZINI" % ff_name, 1 ^ init)

            # CLKINV turns out to be more complicated than origianlly thought
            if isff(cel_prim):
                segmk.add_site_tag(site, "CLKINV", cinv)
                segmk.add_site_tag(site, "NOCLKINV", 1 ^ cinv)
            else:
                segmk.add_site_tag(site, "CLKINV", 1 ^ cinv)
                segmk.add_site_tag(site, "NOCLKINV", cinv)

            # Synchronous vs asynchronous FF
            # Unlike most bits, shared between all CLB FFs
            segmk.add_site_tag(site, "FFSYNC", cel_prim in ('FDSE', 'FDRE'))

            # Latch bit
            # Only applies to LUT6 (non-5) FF's
            if not is5:
                segmk.add_site_tag(site, "LATCH", isl(cel_prim))
            '''
            On name:
            The primitives you listed have a control input to set the FF value to zero (clear/reset),
            the other three primitives have a control input that sets the FF value to one.
            Z => inversion
            '''
            segmk.add_site_tag(
                site, "%s.ZRST" % ff_name,
                cel_prim in ('FDRE', 'FDCE', 'LDCE'))

segmk.compile()
segmk.write()
