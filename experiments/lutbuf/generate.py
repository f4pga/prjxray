#!/usr/bin/env python3

import sys, re

sys.path.append("../../../utils/")
from segmaker import segmaker

segmk = segmaker("design.bits")

print("Loading tags from design.txt")
with open("design.txt", "r") as f:
    for line in f:
        '''
		puts $fp "$type $tile $grid_x $grid_y $lut $lut_type $used"
        CLBLM_R CLBLM_R_X11Y100 33 51 SLICE_X14Y100/B5LUT LUT_OR_MEM5 0
        CLBLM_R CLBLM_R_X11Y100 33 51 SLICE_X14Y100/A6LUT LUT_OR_MEM6 1
        CLBLM_R CLBLM_R_X11Y100 33 51 SLICE_X14Y100/A5LUT LUT_OR_MEM5 1
        CLBLM_R CLBLM_R_X11Y100 33 51 SLICE_X15Y100/D6LUT LUT6 0
        CLBLM_R CLBLM_R_X11Y100 33 51 SLICE_X15Y100/D5LUT LUT5 0
        CLBLM_R CLBLM_R_X11Y100 33 51 SLICE_X15Y100/C6LUT LUT6 1
        
        Lets just keep LUT6 for now
        LUT6
        LUT_OR_MEM6
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
        used = int(line[6])
        if lut_type not in ('LUT6', 'LUT_OR_MEM6'):
            continue

        which = lut_name[0]
        segmk.addtag(site, lut_type + '.' + "%cANY" % which, used)

segmk.compile()
segmk.write()

