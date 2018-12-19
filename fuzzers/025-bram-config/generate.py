#!/usr/bin/env python3

import json

from prjxray.segmaker import Segmaker
from prjxray import verilog


def isinv_tags(segmk, ps, site):
    # all of these bits are inverted
    ks = [
        ('IS_CLKARDCLK_INVERTED', 'ZINV_CLKARDCLK'),
        ('IS_CLKBWRCLK_INVERTED', 'ZINV_CLKBWRCLK'),
        ('IS_ENARDEN_INVERTED', 'ZINV_ENARDEN'),
        ('IS_ENBWREN_INVERTED', 'ZINV_ENBWREN'),
        ('IS_RSTRAMARSTRAM_INVERTED', 'ZINV_RSTRAMARSTRAM'),
        ('IS_RSTRAMB_INVERTED', 'ZINV_RSTRAMB'),
        ('IS_RSTREGARSTREG_INVERTED', 'ZINV_RSTREGARSTREG'),
        ('IS_RSTREGB_INVERTED', 'ZINV_RSTREGB'),
    ]
    for param, tagname in ks:
        segmk.add_site_tag(site, tagname, 1 ^ verilog.parsei(ps[param]))


def bus_tags(segmk, ps, site):
    '''
    parameter DOA_REG = 1'b0;
    parameter DOB_REG = 1'b0;
    parameter SRVAL_A = 18'b0;
    parameter SRVAL_B = 18'b0;
    parameter INIT_A = 18'b0;
    parameter INIT_B = 18'b0;
    '''
    for param, tagname in [('SRVAL_A', 'ZSRVAL_A'), ('SRVAL_B', 'ZSRVAL_B'),
                           ('INIT_A', 'ZINIT_A'), ('INIT_B', 'ZINIT_B')]:
        bitstr = verilog.parse_bitstr(ps[param])
        ab = param[-1]
        # Are all bits present?
        hasparity = ps['READ_WIDTH_' + ab] == 18
        for i in range(18):
            # Magic bit positions from experimentation
            # we could just only solve when parity, but this check documents the fine points a bit better
            if hasparity or i not in (1, 9):
                segmk.add_site_tag(site, '%s[%u]' % (param, i), 1 ^ bitstr[i])


def rw_width_tags(segmk, ps, site):
    '''
    Y0.READ_WIDTH_A
    width   001_03  001_04  001_05
    1       0       0       0
    2       1       0       0
    4       0       1       0
    9       1       1       0
    18      0       0       1
    '''
    '''
    for param, vals in {
            "READ_WIDTH_A": [1, 2, 4, 9, 18],
            "READ_WIDTH_B": [1, 2, 4, 9, 18],
            "WRITE_WIDTH_A": [1, 2, 4, 9, 18],
            "WRITE_WIDTH_B": [1, 2, 4, 9, 18],
            }.items():
        set_val = int(ps[param])
        for val in vals:
            has = set_val == val
            segmk.add_site_tag(site, '%s_B0' % (param), has)
    '''
    for param in ["READ_WIDTH_A", "READ_WIDTH_B", "WRITE_WIDTH_A",
                  "WRITE_WIDTH_B"]:
        set_val = int(ps[param])
        # Multiple bits (not one hot)
        # segmk.add_site_tag(site, '%s_B0' % (param), set_val in (2, 9))
        # segmk.add_site_tag(site, '%s_B1' % (param), set_val in (4, 9))
        # segmk.add_site_tag(site, '%s_B2' % (param), set_val in (18, ))

        # 1 is special in that its all 0's
        # diff only against that
        segmk.add_site_tag(site, '%s_%u' % (param, 1), set_val != 1)
        for widthn in [2, 4, 9, 18]:
            if set_val == 1:
                segmk.add_site_tag(site, '%s_%u' % (param, widthn), False)
            elif set_val == widthn:
                segmk.add_site_tag(site, '%s_%u' % (param, widthn), True)


def write_mode_tags(segmk, ps, site):
    for param in ["WRITE_MODE_A", "WRITE_MODE_B"]:
        set_val = verilog.unquote(ps[param])
        # WRITE_FIRST: no bits set
        segmk.add_site_tag(
            site, '%s_READ_FIRST' % (param), set_val == "READ_FIRST")
        segmk.add_site_tag(
            site, '%s_NO_CHANGE' % (param), set_val == "NO_CHANGE")


def run():

    segmk = Segmaker("design.bits")
    #segmk.set_def_bt('BLOCK_RAM')

    print("Loading tags")
    f = open('params.jl', 'r')
    f.readline()
    for l in f:
        j = json.loads(l)
        ps = j['params']
        assert j['module'] == 'my_RAMB18E1'
        site = verilog.unquote(ps['LOC'])
        #print('site', site)

        isinv_tags(segmk, ps, site)
        bus_tags(segmk, ps, site)
        rw_width_tags(segmk, ps, site)
        write_mode_tags(segmk, ps, site)

    def bitfilter(frame, bit):
        # rw_width_tags() aliasing interconnect on large widths
        return frame not in (20, 21)

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


run()
