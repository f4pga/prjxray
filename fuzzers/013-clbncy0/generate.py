#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
from prjxray import util

segmk = Segmaker(util.get_db_root(), "design.bits")

print("Loading tags")
'''
module,loc,bel,n
clb_NCY0_MX,SLICE_X12Y100,A6LUT,3
clb_NCY0_O5,SLICE_X16Y100,C6LUT,0
clb_NCY0_O5,SLICE_X17Y100,A6LUT,2
'''
f = open('params.csv', 'r')
f.readline()
for l in f:
    module, loc, bel, n = l.split(',')
    n = int(n)
    # A, B, etc
    which = bel[0]

    # One bit, set on O5
    segmk.add_site_tag(loc, "CARRY4.%cCY0" % which, module == 'clb_NCY0_O5')
segmk.compile()
segmk.write()
