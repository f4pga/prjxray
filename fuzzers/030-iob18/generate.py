#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2022  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

from prjxray.segmaker import Segmaker
from prjxray import segmaker
from prjxray import verilog
import os
import json
import csv

from iostandards import *

def bitfilter(frame, word):
    return 38 <= frame

def mk_drive_opt(iostandard, drive):
    if drive is None:
        drive = '_FIXED'
    return '{}.DRIVE.I{}'.format(iostandard, drive)

def drives_for_iostandard(iostandard):
    if iostandard in ['LVCMOS18', 'LVCMOS15']:
        drives = [2, 4, 6, 8, 12, 16]
    elif iostandard == 'LVCMOS12':
        drives = [2, 4, 6, 8]
    elif iostandard in SSTL + DIFF_SSTL:
        return ['_FIXED']
    else:
        assert False, "this line should be unreachable"

    return drives

STEPDOWN_IOSTANDARDS   = LVCMOS + SSTL
IBUF_LOW_PWR_SUPPORTED = LVDS + SSTL
ONLY_DIFF_IOSTANDARDS  = LVDS


def main():
    # Create map of iobank -> sites
    iobanks = {}
    site_to_iobank = {}
    iobank_iostandards = {}
    with open(os.path.join(os.getenv('FUZDIR'), 'build', 'iobanks.txt')) as f:
        for l in f:
            iob_site, iobank = l.strip().split(',')
            iobank = int(iobank)

            if iobank not in iobanks:
                iobanks[iobank] = set()

            iobanks[iobank].add(iob_site)
            assert iob_site not in site_to_iobank
            site_to_iobank[iob_site] = iobank

    for iobank in iobanks:
        iobank_iostandards[iobank] = set()

    # Load a list of PUDC_B pin function tiles. They are configured differently
    # by the vendor tools so need to be skipped
    pudc_tiles = set()
    with open(os.path.join(os.getenv('FUZDIR'), 'build',
                           'pudc_sites.csv')) as f:
        for l in csv.DictReader(f):
            pudc_tiles.add(l["tile"])

    print("Loading tags")
    segmk = Segmaker("design.bits")
    '''
    port,site,tile,pin,slew,drive,pulltype
    di[0],IOB_X1Y107,RIOB18_X1Y107,AF4,PULLDOWN
    di[10],IOB_X1Y147,RIOB18_X1Y147,U5,PULLUP
    '''
    with open('params.json', 'r') as f:
        design = json.load(f)

        diff_pairs = set()
        for d in design['tiles']:
            iostandard = verilog.unquote(d['IOSTANDARD'])
            if iostandard.startswith('DIFF_'):
                diff_pairs.add(d['pair_site'])

        for d in design['tiles']:
            site = d['site']
            tile = d['tile']

            if tile in pudc_tiles:
                continue

            if site in diff_pairs:
                continue

            iostandard = verilog.unquote(d['IOSTANDARD'])
            if iostandard.startswith('DIFF_'):
                iostandard = iostandard[5:]

            iobank_iostandards[site_to_iobank[site]].add(iostandard)

            only_diff_io = iostandard in ONLY_DIFF_IOSTANDARDS

            if d['type'] is None:
                segmk.add_site_tag(site, 'INOUT', 0)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.IN'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.IN_ONLY'.format(iostandard), 0)
            elif d['type'] == 'IBUF':
                segmk.add_site_tag(site, 'INOUT', 0)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN_DIFF'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.IN_ONLY'.format(iostandard), 1)
                segmk.add_tile_tag(tile, 'IN_DIFF', 0)

                if iostandard in IBUF_LOW_PWR_SUPPORTED:
                    segmk.add_site_tag(site, 'IBUF_LOW_PWR', d['IBUF_LOW_PWR'])
                    segmk.add_site_tag(site, 'ZIBUF_LOW_PWR', 1 ^ d['IBUF_LOW_PWR'])

            elif d['type'] == 'IBUFDS':
                psite = d['pair_site']
                segmk.add_site_tag(site,  'INOUT', 0)
                segmk.add_site_tag(site,  '{}.IN_USE'.format(iostandard), 1)
                segmk.add_site_tag(site,  '{}.IN'.format(iostandard), 1)
                segmk.add_site_tag(site,  '{}.IN_DIFF'.format(iostandard), 1)
                segmk.add_site_tag(psite, '{}.IN_DIFF'.format(iostandard), 1)
                segmk.add_site_tag(site,  '{}.OUT'.format(iostandard), 0)
                segmk.add_site_tag(site,  '{}.IN_ONLY'.format(iostandard), 1)
                segmk.add_tile_tag(tile,  'IN_DIFF', 1)

                if iostandard in IBUF_LOW_PWR_SUPPORTED:
                    segmk.add_tile_tag(tile, 'DIFF.IBUF_LOW_PWR', d['IBUF_LOW_PWR'])
                    segmk.add_tile_tag(tile, 'DIFF.ZIBUF_LOW_PWR', 1 ^ d['IBUF_LOW_PWR'])

            elif d['type'] == 'OBUF':
                segmk.add_site_tag(site, 'INOUT', 0)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 1)
                segmk.add_tile_tag(tile, 'OUT_DIFF', 0)

            elif d['type'] == 'OBUFDS':
                segmk.add_site_tag(site, 'INOUT', 0)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 1)
                segmk.add_tile_tag(tile, 'OUT_DIFF', 1 and not only_diff_io)
                segmk.add_tile_tag(tile, 'OUT_TDIFF', 0)

            elif d['type'] == 'OBUFTDS':
                segmk.add_site_tag(site, 'INOUT', 0)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN'.format(iostandard), 0)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 1)
                segmk.add_tile_tag(tile, 'OUT_DIFF', 1 and not only_diff_io)
                segmk.add_tile_tag(tile, 'OUT_TDIFF', 1 and not only_diff_io)

            elif d['type'] == 'IOBUF_DCIEN':
                segmk.add_site_tag(site, 'INOUT', 1)
                segmk.add_site_tag(site, '{}.IN_USE'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.IN'.format(iostandard), 1)
                segmk.add_site_tag(site, '{}.OUT'.format(iostandard), 1)


            if d['type'] is not None:
                segmaker.add_site_group_zero(
                    segmk, site, "PULLTYPE.",
                    ("NONE", "KEEPER", "PULLDOWN", "PULLUP"), "PULLDOWN",
                    verilog.unquote(d['PULLTYPE']))

            if d['type'] in [None, 'IBUF', 'IBUFDS']:
                continue

            drive_opts = set()
            for opt in LVCMOS:
                for drive_opt in ("2", "4", "6", "8", "12", "16"):
                    if drive_opt in ["12", "16"] and opt == "LVCMOS12":
                        continue

                    drive_opts.add(mk_drive_opt(opt, drive_opt))

            for sstl in SSTL:
                drive_opts.add(mk_drive_opt(sstl, None))

            drive_opts.add(mk_drive_opt("LVDS", None))

            segmaker.add_site_group_zero(
                segmk, site, '', drive_opts, mk_drive_opt('LVCMOS25', '12'),
                mk_drive_opt(iostandard, d['DRIVE']))

            if d['SLEW']:
                for opt in ["SLOW", "FAST"]:
                    segmk.add_site_tag(
                        site, iostandard + ".SLEW." + opt,
                        opt == verilog.unquote(d['SLEW']))

            if 'ibufdisable_wire' in d:
                segmk.add_site_tag(
                    site, 'IBUFDISABLE.I', d['ibufdisable_wire'] != '0')

            if 'dcitermdisable_wire' in d:
                segmk.add_site_tag(
                    site, 'DCITERMDISABLE.I', d['dcitermdisable_wire'] != '0')

    site_to_cmt = {}
    site_to_tile = {}
    tile_to_cmt = {}
    cmt_to_idelay = {}
    with open(os.path.join(os.getenv('FUZDIR'), 'build', 'cmt_regions.csv')) as f:
        for l in f:
            site, tile, cmt = l.strip().split(',')
            site_to_tile[site] = tile

            site_to_cmt[site] = cmt
            tile_to_cmt[tile] = cmt

            # Given IDELAYCTRL's are only located in HCLK_IOI tiles, and
            # there is only on HCLK_IOI tile per CMT, update
            # CMT -> IDELAYCTRL / tile map.
            if 'IDELAYCTRL' in site:
                assert cmt not in cmt_to_idelay
                cmt_to_idelay[cmt] = site, tile

    # For each IOBANK with an active VREF set the feature
    cmt_vref_active = set()
    with open('iobank_vref.csv') as f:
        for l in f:
            iobank, vref = l.strip().split(',')
            iobank = int(iobank)

            cmt = None
            for cmt_site in iobanks[iobank]:
                if cmt_site in site_to_cmt:
                    cmt = site_to_cmt[cmt_site]
                    break

            if cmt is None:
                continue

            cmt_vref_active.add(cmt)

            _, hclk_cmt_tile = cmt_to_idelay[cmt]

            opt = 'VREF.V_{:d}_MV'.format(int(float(vref) * 1000))
            segmk.add_tile_tag(hclk_cmt_tile, opt, 1)

    for iobank in iobank_iostandards:
        if len(iobank_iostandards[iobank]) == 0:
            continue

        for cmt_site in iobanks[iobank]:
            if cmt_site in site_to_cmt:
                cmt = site_to_cmt[cmt_site]
                break

        if cmt is None:
            continue

        _, hclk_cmt_tile = cmt_to_idelay[cmt]

        assert len(iobank_iostandards[iobank]) == 1, iobank_iostandards[iobank]

        iostandard = list(iobank_iostandards[iobank])[0]
        segmk.add_tile_tag(
            hclk_cmt_tile, 'ONLY_DIFF_IN_USE',
            iostandard in ONLY_DIFF_IOSTANDARDS)

    # For IOBANK's with no active VREF, clear all VREF options.
    for cmt, (_, hclk_cmt_tile) in cmt_to_idelay.items():
        if cmt in cmt_vref_active:
            continue

        for vref in (
                .600,
                .675,
                .75,
                .90,
        ):
            opt = 'VREF.V_{:d}_MV'.format(int(vref * 1000))
            segmk.add_tile_tag(hclk_cmt_tile, opt, 0)

    segmk.compile(bitfilter=bitfilter)
    segmk.write(allow_empty=True)

if __name__ == "__main__":
    main()
