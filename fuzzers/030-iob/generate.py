#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
from prjxray import segmaker

segmk = Segmaker("design.bits")

print("Loading tags")
'''
port,site,tile,pin,slew,drive,pulltype
di[0],IOB_X0Y107,LIOB33_X0Y107,A21,PULLDOWN
di[10],IOB_X0Y147,LIOB33_X0Y147,F14,PULLUP
'''
f = open('design.csv', 'r')
f.readline()
for l in f:
    l = l.strip()
    port, site, tile, pin, iostandard, slew, drive, pulltype = l.split(',')
    '''
    LVCMOS25
    SLEW    38_82   38_86   39_81   39_85
    SLOW      X       X       X       X
    FAST

    DRIVE   38_64   38_66   38_72   38_74   39_65   39_73
    4         X        X                              X
    8                         X
    12
    16                                X       X       X

    PULLTYPE    28  29  30
    NONE                X
    KEEPER      X       X
    PULLDOWN
    PULLUP          X   X
    '''
    if pulltype == "":
        pulltype = "NONE"
    segmaker.add_site_group_zero(
        segmk, site, "PULLTYPE.", ("NONE", "KEEPER", "PULLDOWN", "PULLUP"),
        "PULLDOWN", pulltype)

    segmaker.add_site_group_zero(
        segmk, site, iostandard + ".DRIVE.", ("4", "8", "12", "16"), "12",
        drive)
    segmaker.add_site_group_zero(
        segmk, site, "SLEW.", ("SLOW", "FAST"), "FAST", slew)
segmk.compile()
segmk.write()
