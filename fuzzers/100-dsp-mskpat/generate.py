#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
import csv

segmk = Segmaker("design.bits", verbose=True)

print("Loading tags")
with open('params.csv', 'r') as f:
    for d in csv.DictReader(f):
        dsp = "DSP_0" if d['SITE'][-1] in "02468" else "DSP_1"

        acascreg = int(d['ACASCREG'])
        segmk.add_site_tag(
            d['SITE'], "%s.ZACASCREG[0]" % (dsp), ~(acascreg >> 0) & 1)
        segmk.add_site_tag(
            d['SITE'], "%s.ZACASCREG[1]" % (dsp), ~(acascreg >> 1) & 1)

        adreg = int(d['ADREG'])
        segmk.add_site_tag(d['SITE'], "%s.ADREG[0]" % (dsp), adreg & 1)

        alumodereg = int(d['ALUMODEREG'])
        segmk.add_site_tag(
            d['SITE'], "%s.ZALUMODEREG[0]" % (dsp), ~alumodereg & 1)

        areg = int(d['AREG'])
        segmk.add_site_tag(d['SITE'], "%s.ZAREG[0]" % (dsp), ~(areg >> 0) & 1)
        segmk.add_site_tag(d['SITE'], "%s.ZAREG[1]" % (dsp), ~(areg >> 1) & 1)

        bcascreg = int(d['BCASCREG'])
        segmk.add_site_tag(
            d['SITE'], "%s.ZBCASCREG[0]" % (dsp), ~(bcascreg >> 0) & 1)
        segmk.add_site_tag(
            d['SITE'], "%s.ZBCASCREG[1]" % (dsp), ~(bcascreg >> 1) & 1)

        breg = int(d['BREG'])
        segmk.add_site_tag(d['SITE'], "%s.ZBREG[0]" % (dsp), ~(breg >> 0) & 1)
        segmk.add_site_tag(d['SITE'], "%s.ZBREG[1]" % (dsp), ~(breg >> 1) & 1)

        carryinreg = int(d['CARRYINREG'])
        segmk.add_site_tag(d['SITE'], "%s.ZCARRYINREG[0]" % (dsp), ~carryinreg)

        carryinselreg = int(d['CARRYINSELREG'])
        segmk.add_site_tag(
            d['SITE'], "%s.ZCARRYINSELREG[0]" % (dsp), ~carryinselreg)

        creg = int(d['CREG'])
        segmk.add_site_tag(d['SITE'], "%s.ZCREG[0]" % (dsp), ~creg)

        dreg = int(d['DREG'])
        segmk.add_site_tag(d['SITE'], "%s.DREG[0]" % (dsp), dreg)

        inmodereg = int(d['INMODEREG'])
        segmk.add_site_tag(d['SITE'], "%s.ZINMODEREG[0]" % (dsp), ~inmodereg)

        mreg = int(d['MREG'])
        segmk.add_site_tag(d['SITE'], "%s.ZMREG[0]" % (dsp), ~mreg)

        opmodereg = int(d['OPMODEREG'])
        segmk.add_site_tag(d['SITE'], "%s.ZOPMODEREG[0]" % (dsp), ~opmodereg)

        preg = int(d['PREG'])
        segmk.add_site_tag(d['SITE'], "%s.ZPREG[0]" % (dsp), ~preg)

        a_input = str(d['A_INPUT'])
        segmk.add_site_tag(
            d['SITE'], "%s.ZA_INPUT[0]" % (dsp),
            (0 if a_input == "DIRECT" else 1))

        b_input = str(d['B_INPUT'])
        segmk.add_site_tag(
            d['SITE'], "%s.ZB_INPUT[0]" % (dsp),
            (0 if b_input == "DIRECT" else 1))

        use_dport = str(d['USE_DPORT'])
        segmk.add_site_tag(
            d['SITE'], "%s.USE_DPORT[0]" % (dsp),
            (0 if use_dport == "FALSE" else 1))

        use_mult = str(d['USE_MULT'])
        if use_mult == "NONE":
            segmk.add_site_tag(d['SITE'], "%s.USE_MULT[0]" % (dsp), 0)
            segmk.add_site_tag(d['SITE'], "%s.ZUSE_MULT[1]" % (dsp), ~0)
        elif use_mult == "MULTIPLY":
            segmk.add_site_tag(d['SITE'], "%s.USE_MULT[0]" % (dsp), 0)
            segmk.add_site_tag(d['SITE'], "%s.ZUSE_MULT[1]" % (dsp), ~1)
        elif use_mult == "DYNAMIC":
            segmk.add_site_tag(d['SITE'], "%s.USE_MULT[0]" % (dsp), 1)
            segmk.add_site_tag(d['SITE'], "%s.ZUSE_MULT[1]" % (dsp), ~1)

        use_simd = str(d['USE_SIMD'])
        if use_simd == "ONE48":
            segmk.add_site_tag(d['SITE'], "%s.USE_SIMD[0]" % (dsp), 0)
            segmk.add_site_tag(d['SITE'], "%s.USE_SIMD[1]" % (dsp), 0)
        elif use_simd == "TWO24":
            segmk.add_site_tag(d['SITE'], "%s.USE_SIMD[0]" % (dsp), 0)
            segmk.add_site_tag(d['SITE'], "%s.USE_SIMD[1]" % (dsp), 1)
        elif use_simd == "FOUR12":
            segmk.add_site_tag(d['SITE'], "%s.USE_SIMD[0]" % (dsp), 1)
            segmk.add_site_tag(d['SITE'], "%s.USE_SIMD[1]" % (dsp), 1)

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

        sel_mask = str(d['SEL_MASK'])
        if sel_mask == "MASK":
            segmk.add_site_tag(d['SITE'], "%s.SEL_MASK[0]" % (dsp), 0)
            segmk.add_site_tag(d['SITE'], "%s.SEL_MASK[1]" % (dsp), 0)
            segmk.add_site_tag(d['SITE'], "%s.SEL_MASK[2]" % (dsp), 0)
        elif sel_mask == "C":
            segmk.add_site_tag(d['SITE'], "%s.SEL_MASK[0]" % (dsp), 0)
            segmk.add_site_tag(d['SITE'], "%s.SEL_MASK[1]" % (dsp), 1)
            segmk.add_site_tag(d['SITE'], "%s.SEL_MASK[2]" % (dsp), 0)
        elif sel_mask == "ROUNDING_MODE1":
            segmk.add_site_tag(d['SITE'], "%s.SEL_MASK[0]" % (dsp), 1)
            segmk.add_site_tag(d['SITE'], "%s.SEL_MASK[1]" % (dsp), 1)
            segmk.add_site_tag(d['SITE'], "%s.SEL_MASK[2]" % (dsp), 0)
        elif sel_mask == "ROUNDING_MODE2":
            segmk.add_site_tag(d['SITE'], "%s.SEL_MASK[0]" % (dsp), 0)
            segmk.add_site_tag(d['SITE'], "%s.SEL_MASK[1]" % (dsp), 0)
            segmk.add_site_tag(d['SITE'], "%s.SEL_MASK[2]" % (dsp), 1)

        sel_pattern = str(d['SEL_PATTERN'])
        segmk.add_site_tag(
            d['SITE'], "%s.ZSEL_PATTERN[0]" % (dsp),
            (0 if sel_pattern == "PATTERN" else 1))

        use_pattern_detect = str(d['USE_PATTERN_DETECT'])
        segmk.add_site_tag(
            d['SITE'], "%s.USE_PATTERN_DETECT[0]" % (dsp),
            (0 if use_pattern_detect == "PATDET" else 1))

segmk.compile()
segmk.write()
