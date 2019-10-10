#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
import csv

segmk = Segmaker("design.bits", verbose=True)

print("Loading tags")
with open('params.csv', 'r') as f:
    for d in csv.DictReader(f):
        dsp = "DSP_0" if d['SITE'][-1] in "02468" else "DSP_1"

        a_input = str(d['A_INPUT'])
        segmk.add_site_tag(
            d['SITE'], "%s.ZA_INPUT[0]" % (dsp),
            (0 if a_input == "DIRECT" else 1))

        b_input = str(d['B_INPUT'])
        segmk.add_site_tag(
            d['SITE'], "%s.ZB_INPUT[0]" % (dsp),
            (0 if b_input == "DIRECT" else 1))

        autoreset_patdet = str(d['AUTORESET_PATDET'])
        if autoreset_patdet == "RESET_MATCH":
            segmk.add_site_tag(d['SITE'], "%s.AUTO_RESET_PATDET[0]" % (dsp), 0)
            segmk.add_site_tag(
                d['SITE'], "%s.ZAUTO_RESET_PATDET[1]" % (dsp), 1)
        elif autoreset_patdet == "NO_RESET":
            segmk.add_site_tag(d['SITE'], "%s.AUTO_RESET_PATDET[0]" % (dsp), 0)
            segmk.add_site_tag(
                d['SITE'], "%s.ZAUTO_RESET_PATDET[1]" % (dsp), 0)
        elif autoreset_patdet == "RESET_NOT_MATCH":
            segmk.add_site_tag(d['SITE'], "%s.AUTO_RESET_PATDET[0]" % (dsp), 1)
            segmk.add_site_tag(
                d['SITE'], "%s.ZAUTO_RESET_PATDET[1]" % (dsp), 1)

        mask = int(d['MASK'])
        pattern = int(d['PATTERN'])

        for i in range(48):
            segmk.add_site_tag(
                d['SITE'], "%s.MASK[%d]" % (dsp, i), (mask >> i) & 1)
            segmk.add_site_tag(
                d['SITE'], "%s.PATTERN[%d]" % (dsp, i), (pattern >> i) & 1)

segmk.compile()
segmk.write()
