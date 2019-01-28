#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
import csv

segmk = Segmaker("design.bits", verbose=True)

print("Loading tags")
with open('params.csv', 'r') as f:
    for d in csv.DictReader(f):
        dsp = "DSP_0" if d['site'][-1] in "02468" else "DSP_1"

        mask = int(d['mask'])
        pattern = int(d['pattern'])

        for i in range(48):
            segmk.add_site_tag(d['site'], "%s.MASK[%d]" % (dsp, i), (mask >> i) & 1)
            segmk.add_site_tag(
                d['site'], "%s.PATTERN[%d]" % (dsp, i), (pattern >> i) & 1)

segmk.compile()
segmk.write()
