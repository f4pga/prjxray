#!/usr/bin/env python3

import sys, re

sys.path.append("../../../utils/")
from segmaker import segmaker

segmk = segmaker("design.bits")

ffprims = (
        'FD',
        'FD_1',
        'FDC',
        'FDC_1',
        'FDCE',
        'FDCE_1',
        'FDE',
        'FDE_1',
        'FDP',
        'FDP_1',
        'FDPE',
        'FDPE_1',
        'FDR',
        'FDR_1',
        'FDRE',
        'FDRE_1',
        'FDS',
        'FDS_1',
        'FDSE',
        'FDSE_1',
        )
ffprims = (
        'FDRE',
        'FDSE',
        'FDCE',
        'FDPE',
        )

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
        site_ff_name = line[4]
        site, ff_name = site_ff_name.split('/')
        ff_type = line[5]
        used = int(line[6])
        ref_name = None
        cel_name = None
        if used:
            cel_name = line[7]
            ref_name = line[8]
            # 1'b1
            # cinv = int(line[9][-1])
            cinv = int(line[9])

        which = ff_name[0]
        # Reduced test for now
        #if ff_name != 'AFF':
        #    continue

        #segmk.addtag(site, "FF_USED", used)
        if 0:
            # If unused mark all primitives as not present
            # Otherwise mark the primitive we are using
            for ffprim in ffprims:
                if not used:
                    segmk.addtag(site, "FF_%s" % ffprim, 0)
                elif ref_name == ffprim:
                    segmk.addtag(site, "FF_%s" % ffprim, 1)

        # Theory:
        # FDPE represents none of the FF specific bits used
        # FDRE has none of the bits used
        if 1:
            # If unused mark all primitives as not present
            # Otherwise mark the primitive we are using
            # Should yield 3 bits
            if used:
                if ref_name == 'FDPE':
                    segmk.addtag(site, "%s.PRIM" % ff_name, 0)
                if ref_name == 'FDRE':
                    segmk.addtag(site, "%s.PRIM" % ff_name, 1)

segmk.compile()
segmk.write()

