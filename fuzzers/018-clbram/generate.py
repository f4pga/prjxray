#!/usr/bin/env python3

import sys, re

sys.path.append("../../../utils/")
from segmaker import segmaker

segmk = segmaker("design.bits")

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
my_ram_N,SLICE_X12Y100,SRL16E,SRLC32E,SRLC32E,SRLC32E
my_ram_N,SLICE_X12Y101,SRLC32E,SRL16E,SRL16E,SRLC32E
my_ram_N,SLICE_X12Y102,SRLC32E,SRL16E,SRLC32E,RAM32X1S
my_RAM256X1S,SLICE_X12Y103,,,,
'''
f = open('params.csv', 'r')
f.readline()
for l in f:
    l = l.strip()
    module,loc,bela,belb,belc,beld = l.split(',')
    bels = [bela,belb,belc,beld]
    if module in greedy_modules:
        '''
        my_RAM128X1D #(.LOC("SLICE_X12Y100"))
            WA7USED
        my_RAM128X1S #(.LOC("SLICE_X12Y102"))
            WA7USED
        my_RAM256X1S #(.LOC("SLICE_X12Y103"))
            WA7USED, WA8USED
        '''
        which = 'D'
        if 1:
            print(loc, 1)
            segmk.addtag(loc, "WA7USED", 1)
            segmk.addtag(loc, "WA8USED", module == 'my_RAM256X1S')
    else:
        '''
        LUTD
                    01_23   01_59   30_47   31_47
        SRL16E      1       1       1
        SRLC32E     1               1
        RAM32X1S    1       1               1
        RAM64X1S    1                       1

        01_23: WEMUX.CE (more info needed)
        01_59: half sized memory
        30_47: SRL mode
        31_47: RAM mode
        '''
        for which, bel in zip('ABCD', bels):
            print(which, bel)
            segmk.addtag(loc, "%sLUT.SMALL" % which, bel in ('SRL16E', 'RAM32X1S'))
            segmk.addtag(loc, "%sLUT.SRL" % which, bel in ('SRL16E', 'SRLC32E'))
            # Only valid in D
            if which == 'D':
                segmk.addtag(loc, "%sLUT.RAM" % which, bel in ('RAM32X1S', 'RAM64X1S'))
        if 1:
            segmk.addtag(loc, "WA7USED", 0)
            #segmk.addtag(loc, "WA7USED", 1)
            print(loc, 0)
            segmk.addtag(loc, "WA8USED", 0)
            segmk.addtag(loc, "WEMUX.CE", bels != ['LUT6', 'LUT6', 'LUT6', 'LUT6'])

segmk.compile()
segmk.write()

