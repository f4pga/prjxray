#!/usr/bin/env python3

import sys, re

sys.path.append("../../../utils/")
from segmaker import segmaker

segmk = segmaker("design.bits")

print("Loading tags from design.txt")
with open("design.txt", "r") as f:
    for line in f:
        '''
        puts $fp "$type $tile $grid_x $grid_y $lut $lut_type"
        CLBLM_L CLBLM_L_X10Y112 30 39 SLICE_X13Y112/B5LUT LUT5
        CLBLM_L CLBLM_L_X10Y112 30 39 SLICE_X13Y112/A6LUT LUT6
        CLBLM_L CLBLM_L_X10Y112 30 39 SLICE_X12Y112/C6LUT LUT_OR_MEM6
        CLBLM_L CLBLM_L_X10Y145 30 5 SLICE_X12Y145/D5LUT LUT_OR_MEM5

        updated
        CLBLM_L CLBLM_L_X10Y149 30 1 SLICE_X12Y149/C6LUT LUT_OR_MEM6 SLICEM.C6LUT
        '''
        line = line.split()
        tile_type = line[0]
        tile_name = line[1]
        grid_x = line[2]
        grid_y = line[3]
        # Other code uses BEL name
        site_lut_name = line[4]
        site, lut_name = site_lut_name.split('/')
        lut_type = line[5]
        # SLICEL.A6LUT
        cell_bel = line[6]
        slicelm = cell_bel.split('.')[0]

        which = lut_name[0]
        is_lut5 = lut_type in ('LUT5', 'LUT_OR_MEM5')
        site_mod = site + '.' + slicelm
        site_mod = site
        segmk.addtag(site, slicelm + '.' + "%cLUT5" % which, is_lut5)

segmk.compile()
segmk.write()

