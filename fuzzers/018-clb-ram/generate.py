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

verbose = False

segmk = Segmaker("design.bits")

# Can fit 4 per CLB
# BELable
multi_bels_by = [
    'SRL16E',
    'SRLC32E',
]
# Not BELable
multi_bels_bn = [
    'RAM32X1S',
    'RAM64X1S',
]


def load_tcl():
    f = open('design.csv', 'r')
    f.readline()
    ret = {}
    for l in f:
        l = l.strip()
        tile, site, bel, cell, ref_name, prim_type = l.split(',')
        ret[bel] = ref_name
    return ret


design = load_tcl()

print("Loading tags")
'''
module,loc,bela,belb,belc,beld
my_ram_N,SLICE_X12Y100,SRLC32E,SRL16E,SRLC32E,LUT6
my_ram_N,SLICE_X12Y101,SRLC32E,SRLC32E,SRLC32E,SRLC32E
my_RAM256X1S,SLICE_X12Y102,None,0,,
'''
f = open('params.csv', 'r')
f.readline()
for l in f:
    l = l.strip()
    module, loc, p0, p1, p2, p3 = l.split(',')

    segmk.add_site_tag(
        loc, "WA7USED",
        module in ('my_RAM128X1D', 'my_RAM128X1S_N', 'my_RAM256X1S'))
    segmk.add_site_tag(loc, "WA8USED", module == 'my_RAM256X1S')

    bels_tcl = [design.get("%s/%c6LUT" % (loc, bel), None) for bel in "ABCD"]

    # (a, b, c, d)
    # Size set for RAM32X1S, RAM32X1D, and SRL16E
    size = [0, 0, 0, 0]
    # SRL set for SRL* primitives
    srl = [0, 0, 0, 0]
    # RAM set for RAM* primitives
    ram = [0, 0, 0, 0]

    verbose and print('%s' % loc)
    verbose and print('  %s %s %s %s' % tuple(bels_tcl))

    if module == 'my_ram_N':
        # Each one of: SRL16E, SRLC32E, LUT6
        bels = [p0, p1, p2, p3]
        verbose and print('  %s %s %s %s' % tuple(bels))
        assert bels == bels_tcl

        # Clock Enable (CE) clock gate only enabled if we have clocked elements
        # A pure LUT6 does not, but everything else should
        segmk.add_site_tag(
            loc, "WEMUX.CE", bels != ['LUT6', 'LUT6', 'LUT6', 'LUT6'])

        beli = 0
        for which, bel in zip('ABCD', bels):
            if bel == 'SRL16E':
                size[beli] = 1
            if bel in ('SRL16E', 'SRLC32E'):
                srl[beli] = 1
            beli += 1
    else:
        n = p0
        if n:
            n = int(n)
        # Unused. Just to un-alias mux
        #_ff = int(p1)

        # Can pack 4 into a CLB
        # D is always occupied first (due to WA/A sharing on D)
        # TODO: maybe investigate ROM primitive for completeness
        pack4 = [
            # (a, b, c, d)
            (0, 0, 0, 1),
            (1, 0, 0, 1),
            (1, 1, 0, 1),
            (1, 1, 1, 1),
        ]
        # Uses CD first
        pack2 = [
            (0, 0, 1, 1),
            (1, 1, 1, 1),
        ]
        has_bel_tcl = tuple([int(bool(x)) for x in bels_tcl])

        # Always use all 4 sites
        if module in ('my_RAM32M', 'my_RAM64M', 'my_RAM128X1D',
                      'my_RAM256X1S'):
            ram = (1, 1, 1, 1)
        # Only can occupy CD I guess
        elif module == 'my_RAM32X1D':
            ram = (0, 0, 1, 1)
        # Uses 2 sites at a time
        elif module in ('my_RAM64X1D_N', 'my_RAM128X1S_N'):
            ram = pack2[n - 1]
        # Uses 1 site at a time
        elif module in ('my_RAM32X1S_N', 'my_RAM64X1S_N'):
            ram = pack4[n - 1]
        else:
            assert (0)
        verbose and print('  %s %s %s %s' % tuple(ram))
        verbose and print('  %s %s %s %s' % tuple(has_bel_tcl))
        # assert ram == ram_tcl
        # Hack: reject if something unexpected got packed in
        # TODO: place dummy LUTs to exclude placement?
        if ram != has_bel_tcl:
            continue

        # All entries here require D
        assert (ram[3])

        if module == 'my_RAM32X1D':
            # Occupies CD
            size[2] = 1
            size[3] = 1
        elif module == 'my_RAM32M':
            size = [1, 1, 1, 1]
        elif module == 'my_RAM32X1S_N':
            size = pack4[n - 1]
            if size != has_bel_tcl:
                continue
        else:
            assert (not module.startswith('my_RAM32'))

    # Now commit bits after marking 1's
    for beli, bel in enumerate('ABCD'):
        segmk.add_site_tag(loc, "%sLUT.RAM" % bel, ram[beli])
        # FIXME: quick fix
        segmk.add_site_tag(loc, "%sLUT.SRL" % bel, srl[beli])
        segmk.add_site_tag(loc, "%sLUT.SMALL" % bel, size[beli])


def bitfilter(frame_idx, bit_idx):
    # Hack to remove aliased PIP bits on CE
    # We should either mix up routing more or exclude previous DB entries
    return (frame_idx, bit_idx) not in [(0, 27), (1, 25), (1, 26), (1, 29)]


segmk.compile(bitfilter=bitfilter)
segmk.write()
