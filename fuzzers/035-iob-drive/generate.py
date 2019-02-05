#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
from prjxray import segmaker

segmk = Segmaker("design.bits")

print("Loading tags")
'''
port,site,tile,pin,val
di[0],IOB_X0Y107,LIOB33_X0Y107,A21,PULLDOWN
di[10],IOB_X0Y147,LIOB33_X0Y147,F14,PULLUP
'''
def add_site_group_zero2(segmk, site, prefix, vals, zero_val, val):
        assert val in vals or val == zero_val, "Got %s, need %s" % (val, vals)

        if val == zero_val:
             pass
        else:
        # Only add the occured symbol
            tag = prefix + val
            segmk.add_site_tag(site, tag, True)

f = open('design.csv', 'r')
f.readline()
for l in f:
    l = l.strip()
    port, site, tile, pin, val = l.split(',')
    '''
    CMOS18
    DRIVE     38_64    38_66    38_72    38_74    39_65    39_73
    4           X        X                                   X
    8                    X        X                 X
    12                   X        X                 X
    16          X        X                          X
    24                            X        X        X

    CMOS33
    DRIVE    26_02_00 26_02_02 26_02_08 26_02_10 27_02_01 27_02_09
    4           X        X                                   X
    8                    X        X                 X
    12          X        X                          X
    16          X                          X                 X
    '''
    '''
    #For CMOS18
    if val == "4":
        segmk.add_site_tag(site, "DRIVE." + val, True)
        segmk.add_site_tag(site, "DRIVE.24", False)
    if val == "8":
        segmk.add_site_tag(site, "DRIVE." + val, True)
        #segmk.add_site_tag(site, "DRIVE.12", True)
    if val == "12":
        segmk.add_site_tag(site, "DRIVE." + val, True)
        #segmk.add_site_tag(site, "DRIVE.8", True)
    if val == "24":
        segmk.add_site_tag(site, "DRIVE." + val, True)
        segmk.add_site_tag(site, "DRIVE.4", False)
    '''
    #LVCMOS12
    #add_site_group_zero2(segmk, site, "DRIVE.", ("4", "8", "12"), "", val)
    #segmaker.add_site_group_zero(segmk, site, "LVCMOS25.DRIVE.", ("4", "8", "12", "16"), "12", val)

    #LVCMOS15
    #segmaker.add_site_group_zero(segmk, site, "LVCMOS15.DRIVE.", ("4", "8", "12", "16"), "12", val)
    #add_site_group_zero2(segmk, site, "LVCMOS15.DRIVE.", ("4", "8", "12", "16"), "12", val)

    #LVCMOS25
    segmaker.add_site_group_zero(segmk, site, "LVCMOS25.DRIVE.", ("4", "8", "12", "16"), "12", val)
    #segmaker.add_site_group_zero(segmk, site, "SLEW.", ("SLOW", "FAST"), "FAST", val)
segmk.compile()
segmk.write()
