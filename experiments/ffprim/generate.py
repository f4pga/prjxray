#!/usr/bin/env python3

from prims import *

import sys, re

sys.path.append("../../../utils/")
from segmaker import segmaker

segmk = segmaker("design.bits")

def ones(l):
    #return l + [x + '_1' for x in l]
    #return sorted(l + [x + '_1' for x in l])
    ret = []
    for x in l:
        ret.append(x)
        ret.append(x + '_1')
    return ret

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
        cel_prim = None
        cel_name = None
        if used:
            cel_name = line[7]
            # ex: FDCE
            cel_prim = line[8]
            # 1'b1
            # cinv = int(line[9][-1])
            cinv = int(line[9])

        which = ff_name[0]
        # Reduced test for now
        #if ff_name != 'AFF':
        #    continue
        
        is5 = '5' in ff_name

        #segmk.addtag(site, "FF_USED", used)
        if 1:
            # If unused mark all primitives as not present
            # Otherwise mark the primitive we are using
            if used:
                segmk.addtag(site, "%s.%s" % (ff_name, cel_prim), 1)
            else:
                for ffprim in ffprims:
                    # FF's don't do 5's
                    if isff(ffprim) or (isl(ffprim) and not is5):
                        segmk.addtag(site, "%s.%s" % (ff_name, ffprim), 0)

        # Theory:
        # FDPE represents none of the FF specific bits used
        # FDRE has all of the bits used
        if 0:
            # If unused mark all primitives as not present
            # Otherwise mark the primitive we are using
            # Should yield 3 bits
            if used:
                if cel_prim == 'FDPE':
                    segmk.addtag(site, "%s.PRIM" % ff_name, 0)
                if cel_prim == 'FDRE':
                    segmk.addtag(site, "%s.PRIM" % ff_name, 1)

        # FF specific test
        # Theory: FDSE and FDCE are the most and least encoded FF's
        if 1:
            # If unused mark all primitives as not present
            # Otherwise mark the primitive we are using
            # Should yield 3 bits
            if used and isff(cel_prim):
                # PRIM1 is now FFSYNC
                #segmk.addtag(site, "%s.PRIM1" % ff_name,
                #    cel_prim in ('FDSE', 'FDRE'))
                segmk.addtag(site, "%s.PRIM2" % ff_name,
                    cel_prim in ('FDCE', 'FDRE'))
        
        # Theory: there are some common enable bits
        '''
                00_48   30_32   30_12   31_03
        FDPE
        FDSE    X
        FDRE    X               X       X
        FDCE                    X       X
        LDCE            X       X       X
        LDPE            X

        00_48 is shared between all X0 FFs
        '''
        if 1 and used:
            segmk.addtag(site, "FFSYNC",
                    cel_prim in ('FDSE', 'FDRE'))

segmk.compile()
segmk.write()

