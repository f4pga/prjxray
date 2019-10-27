#!/usr/bin/env python3

from prjxray.segmaker import Segmaker
from prjxray.verilog import to_int
from prjxray.verilog import quote
import json


def bits_in(value, width):
    bits = []
    for i in range(width):
        bits.append(value & 1)
        value >>= 1
    return bits


def add(segmk, site, dsp, tag, bit, value, invert):
    tag = dsp + '.' + '%s' % ('Z' if invert else '') + tag + '[%u]' % bit
    value = (~value if invert else value)
    value >>= bit
    return segmk.add_site_tag(site, tag, value & 1)


def run():
    segmk = Segmaker("design.bits", verbose=True)

    print("Loading tags")
    with open('params.json', 'r') as fp:
        data = json.load(fp)

    for params in data['instances']:
        dsp = "DSP_0" if params['SITE'][-1] in "02468" else "DSP_1"
        site = params['SITE']

        add(segmk, site, dsp, 'ADREG', 0, to_int(params['ADREG']), 0)
        add(segmk, site, dsp, 'ALUMODEREG', 0, to_int(params['ALUMODEREG']), 1)

        for i in range(2):
            add(segmk, site, dsp, 'AREG', i, to_int(params['AREG']), 1)

        for i in range(2):
            add(segmk, site, dsp, 'ACASCREG', i, to_int(params['ACASCREG']), 1)

        for i in range(2):
            add(segmk, site, dsp, 'BREG', i, to_int(params['BREG']), 1)

        for i in range(2):
            add(segmk, site, dsp, 'BCASCREG', i, to_int(params['BCASCREG']), 1)

        add(segmk, site, dsp, 'CARRYINREG', 0, to_int(params['CARRYINREG']), 1)
        add(
            segmk, site, dsp, 'CARRYINSELREG', 0,
            to_int(params['CARRYINSELREG']), 1)
        add(segmk, site, dsp, 'CREG', 0, to_int(params['CREG']), 1)

        add(segmk, site, dsp, 'DREG', 0, to_int(params['DREG']), 0)
        add(segmk, site, dsp, 'INMODEREG', 0, to_int(params['INMODEREG']), 1)
        add(segmk, site, dsp, 'OPMODEREG', 0, to_int(params['OPMODEREG']), 1)
        add(segmk, site, dsp, 'PREG', 0, to_int(params['PREG']), 1)

        INPUT = {}
        INPUT[quote('DIRECT')] = 0
        INPUT[quote('CASCADE')] = 1

        add(segmk, site, dsp, 'A_INPUT', 0, INPUT[params['A_INPUT']], 0)
        add(segmk, site, dsp, 'B_INPUT', 0, INPUT[params['B_INPUT']], 0)

        BOOL = {}
        BOOL[quote('FALSE')] = 0
        BOOL[quote('TRUE')] = 1

        add(segmk, site, dsp, 'USE_DPORT', 0, BOOL[params['USE_DPORT']], 0)

        SIMD = {}
        SIMD[quote('ONE48')] = 0
        SIMD[quote('TWO24')] = 1
        SIMD[quote('FOUR12')] = 2

        for i in range(2):
            add(segmk, site, dsp, 'USE_SIMD', i, SIMD[params['USE_SIMD']], 0)

        MULT = {}
        MULT[quote('NONE')] = 0
        MULT[quote('MULTIPLY')] = 1
        MULT[quote('DYNAMIC')] = 2

        for i in range(2):
            add(segmk, site, dsp, 'USE_MULT', i, MULT[params['USE_MULT']], 0)

        add(segmk, site, dsp, 'MREG', 0, to_int(params['MREG']), 1)

        AUTORESET = {}
        AUTORESET[quote('NO_RESET')] = 0
        AUTORESET[quote('RESET_NOT_MATCH')] = 1
        AUTORESET[quote('RESET_MATCH')] = 2

        add(
            segmk, site, dsp, 'AUTORESET_PATDET', 0,
            AUTORESET[params['AUTORESET_PATDET']], 0)
        add(
            segmk, site, dsp, 'AUTORESET_PATDET', 1,
            AUTORESET[params['AUTORESET_PATDET']], 1)

        for i in range(48):
            add(segmk, site, dsp, 'MASK', i, to_int(params['MASK']), 0)

        for i in range(48):
            add(segmk, site, dsp, 'PATTERN', i, to_int(params['PATTERN']), 0)

        SEL_MASK = {}
        SEL_MASK[quote('MASK')] = 0
        SEL_MASK[quote('C')] = 1
        SEL_MASK[quote('ROUNDING_MODE1')] = 2
        SEL_MASK[quote('ROUNDING_MODE2')] = 3

        for i in range(2):
            add(
                segmk, site, dsp, 'SEL_MASK', i, SEL_MASK[params['SEL_MASK']],
                0)

        USE_PATTERN_DETECT = {}
        USE_PATTERN_DETECT[quote('NO_PATDET')] = 0
        USE_PATTERN_DETECT[quote('PATDET')] = 1

        add(
            segmk, site, dsp, 'USE_PATTERN_DETECT', 0,
            USE_PATTERN_DETECT[params['USE_PATTERN_DETECT']], 0)

    segmk.compile()
    segmk.write()


if __name__ == '__main__':
    run()
