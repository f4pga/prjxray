#!/usr/bin/env python3

from prjxray.segmaker import Segmaker

segmk = Segmaker("design.bits")

print("Loading tags")
f = open('params.csv', 'r')
f.readline()
for l in f:
    module, loc, loc2 = l.split(',')
    # clb_PRECYINIT_AX => AX
    src = module.replace('clb_PRECYINIT_', '')
    '''
    PRECYINIT
                00_12   30_14   30_13
    1           0       1       0
    AX          1       0       0
    CIN         0       0       1
    0           0       0       0
    '''
    srcs = ('0', '1', 'AX', 'CIN')
    for asrc in srcs:
        segmk.add_site_tag(loc, "PRECYINIT.%s" % asrc, int(src == asrc))

segmk.compile()
segmk.write()
