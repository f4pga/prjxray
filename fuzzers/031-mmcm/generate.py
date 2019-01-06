#!/usr/bin/env python3

import json

from prjxray.segmaker import Segmaker
from prjxray import verilog


def clkout_tags(segmk, ps, site):
    """
    Special bit for value 1 (bypass), all bits off for value 128.
    Two 7 bit counters, sharing LSB (one counter is value+1, inverting the LSB).
    """
    for param, tagname in [('CLKOUT1_DIVIDE', 'ZCLKOUT1_DIVIDE')]:
        value = int(ps[param])

        # bypass bit
        segmk.add_site_tag(site, '%s_NODIV' % param, value == 1)

        bitstr = [int(x) for x in "{0:08b}".format(value)[::-1]]
        bitstr2 = [int(x) for x in "{0:08b}".format(value + 1)[::-1]]
        for i in range(7):
            mybit = bitstr[i]
            mybit2 = bitstr2[i]
            if i == 0:
                # shared (inverted) LSB
                mybit2 = 1 ^ bitstr2[i]
                assert mybit == mybit2, "{} value {} has invalid bit0 at".format(
                    param, value)

            # special cases
            if value == 1:
                if i == 0:
                    mybit = 0
                    mybit2 = 0
                elif i == 1:
                    mybit = 1
            elif value == 128:
                mybit = 0
                mybit2 = 0

            segmk.add_site_tag(site, '%s_CNT0_[%u]' % (param, i), mybit)
            segmk.add_site_tag(site, '%s_CNT1_[%u]' % (param, i), mybit2)


def misc_tags(segmk, ps, site):
    for boolattr in [
            'STARTUP_WAIT',
            "CLKOUT4_CASCADE",
            "CLKFBOUT_USE_FINE_PS",
            "CLKOUT0_USE_FINE_PS",
            "CLKOUT1_USE_FINE_PS",
            "CLKOUT2_USE_FINE_PS",
            "CLKOUT3_USE_FINE_PS",
            #"CLKOUT4_USE_FINE_PS", # several bits are changing, needs investigation
            "CLKOUT5_USE_FINE_PS",
            "CLKOUT6_USE_FINE_PS"
    ]:
        segmk.add_site_tag(site, boolattr, ps[boolattr] == '"TRUE"')


def run():

    segmk = Segmaker("design.bits")

    print("Loading tags")
    f = open('params.jl', 'r')
    f.readline()
    for l in f:
        j = json.loads(l)
        ps = j['params']
        assert j['module'] == 'my_MMCME2_ADV'
        site = verilog.unquote(ps['LOC'])

        clkout_tags(segmk, ps, site)
        misc_tags(segmk, ps, site)

    segmk.compile()
    segmk.write()


run()
