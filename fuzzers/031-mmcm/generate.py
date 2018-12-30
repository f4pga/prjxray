#!/usr/bin/env python3

import json

from prjxray.segmaker import Segmaker
from prjxray import verilog


def clkout_tags(segmk, ps, site):
    """ Notes:
    First bit is only active for value 1, for 1-128 in total 14 bits are toggling.
    The relation is not clear yet, multiplication of the value by 2 does not fully correlate.
    """
    for param, tagname in [('CLKOUT1_DIVIDE', 'ZCLKOUT1_DIVIDE')]:
        # 1-128 => 0-127 for actual 7 bit value
        paramadj = 2 * int(ps[param])
        bitstr = [int(x) for x in "{0:08b}".format(paramadj)[::-1]]
        # FIXME: only bits 0 and 1 resolving
        for i in range(8):
            # for i in range(2):
            #if i in [0, 3, 5]:
            #    mybit = 1 ^ bitstr[i]
            #else:
            mybit = bitstr[i]
            segmk.add_site_tag(site, '%s[%u]' % (param, i), mybit)


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

        #clkout_tags(segmk, ps, site)
        misc_tags(segmk, ps, site)

    segmk.compile()
    segmk.write()


run()
