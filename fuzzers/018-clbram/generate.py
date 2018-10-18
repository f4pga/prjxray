#!/usr/bin/env python3

import sys, re, os

from prjxray.segmaker import Segmaker

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

# Those requiring special resources
# Just make one per module
greedy_modules = [
    'my_RAM128X1D',
    'my_RAM128X1S',
    'my_RAM256X1S',
]

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

    segmk.addtag(
        loc, "WA7USED",
        module in ('my_RAM128X1D', 'my_RAM128X1S', 'my_RAM256X1S'))
    segmk.addtag(loc, "WA8USED", module == 'my_RAM256X1S')

    # (a, b, c, d)
    # Size set for RAM32X1S, RAM32X1D, and SRL16E
    size = [0, 0, 0, 0]
    # SRL set for SRL* primitives
    srl = [0, 0, 0, 0]
    # RAM set for RAM* primitives
    ram = [0, 0, 0, 0]

    if module == 'my_ram_N':
        # Each one of: SRL16E, SRLC32E, LUT6
        bels = [p0, p1, p2, p3]

        # Clock Enable (CE) clock gate only enabled if we have clocked elements
        # A pure LUT6 does not, but everything else should
        segmk.addtag(loc, "WEMUX.CE", bels != ['LUT6', 'LUT6', 'LUT6', 'LUT6'])

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

        # Always use all 4 sites
        if module in ('my_RAM32M', 'my_RAM64M', 'my_RAM128X1D',
                      'my_RAM256X1S'):
            ram = [1, 1, 1, 1]
        # Only can occupy CD I guess
        elif module == 'my_RAM32X1D':
            ram = [0, 0, 1, 1]
        # Uses 2 sites at a time
        elif module in ('my_RAM64X1D_N', 'my_RAM128X1S_N'):
            ram = pack2[n - 1]
        # Uses 1 site at a time
        elif module in ('my_RAM32X1S_N', 'my_RAM64X1S_N'):
            ram = pack4[n - 1]
        else:
            assert (0)

        # All entries here requiare D
        assert (ram[3])

        if module == 'my_RAM32X1D':
            # Occupies CD
            size[2] = 1
            size[3] = 1
        elif module == 'my_RAM32M':
            size = [1, 1, 1, 1]
        elif module == 'my_RAM32X1S_N':
            size = pack4[n - 1]
        else:
            assert (not module.startswith('my_RAM32'))

    # Now commit bits after marking 1's
    for beli, bel in enumerate('ABCD'):
        segmk.addtag(loc, "%sLUT.RAM" % bel, ram[beli])
        segmk.addtag(loc, "%sLUT.SRL" % bel, srl[beli])
        # FIXME
        module == segmk.addtag(loc, "%sLUT.SMALL" % bel, size[beli])


def bitfilter(frame_idx, bit_idx):
    # Hack to remove aliased PIP bits on CE
    # We should either mix up routing more or exclude previous DB entries
    assert os.getenv("XRAY_DATABASE") == "artix7"
    return (frame_idx, bit_idx) not in [(0, 27), (1, 25), (1, 26), (1, 29)]


segmk.compile(bitfilter=bitfilter)
segmk.write()
