#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
from prjxray import segmaker

segmk = Segmaker("design.bits")

print("Loading params")
f = open('params.csv', 'r')
f.readline()
for l in f:
    l = l.strip()
    site, name, dir_, cell = l.split(',')
    segmaker.add_site_group_zero(
        segmk, site, "MACRO.", ("INPUT", "OUTPUT"), "", dir_.upper())

segmk.compile()
segmk.write()
