#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
import os
import random
import math
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import verilog
from prjxray import lut_maker
from prjxray.db import Database


def read_site_to_cmt():
    """ Yields clock sources and which CMT they route within. """
    fuzdir = os.getenv('FUZDIR')
    part = os.getenv('XRAY_PART')

    with open(os.path.join(fuzdir, 'build_{}'.format(part),
                           'cmt_regions.csv')) as f:
        for l in f:
            site, cmt = l.strip().split(',')
            yield (site, cmt)


def todo_pips():
    """ Returns a boolean tuple corresponding to the presence or not
        of a type of PIP in the todo list."""

    is_gtp_channel_left = False
    is_ibufds_left = False
    is_cmt_left = False

    with open("../../todo_all.txt", "r") as todo_file:
        for line in todo_file:
            fields = line.split(".")

            if "HCLK_GTP_CK_IN" not in fields[1]:
                continue

            is_gtp_channel_left |= fields[2].startswith("GTPE2_COMMON")
            is_ibufds_left |= fields[2].startswith("IBUFDS")
            is_cmt_left |= fields[2].startswith("HCLK")

    return (is_gtp_channel_left, is_ibufds_left, is_cmt_left)


class ClockSources(object):
    """ Class for tracking clock sources.
    """

    def __init__(self, limit=14):
        self.sources = {}
        self.source_to_cmt = {}
        self.used_sources_from_cmt = {}
        self.limit = limit

    def add_clock_source(self, source, cmt):
        """ Adds a source from a specific CMT.

        """
        if cmt not in self.sources:
            self.sources[cmt] = []

        self.sources[cmt].append(source)
        self.source_to_cmt[source] = cmt

    def sources_depleted(self, cmt):
        if cmt in self.sources:
            if cmt not in self.used_sources_from_cmt:
                return False

            return self.sources[cmt] == self.used_sources_from_cmt[cmt]

        return True

    def get_random_source(self, cmt, no_repeats=True):
        """ Get a random source that is routable to the specific CMT.

        get_random_source will return a source that is either cmt='ANY',
        cmt equal to the input CMT, or the adjecent CMT.

        """

        choices = []

        if cmt in self.sources:
            choices.extend(self.sources[cmt])

        random.shuffle(choices)
        for source in choices:

            source_cmt = self.source_to_cmt[source]

            if source_cmt not in self.used_sources_from_cmt:
                self.used_sources_from_cmt[source_cmt] = set()

            if no_repeats and source in self.used_sources_from_cmt[source_cmt]:
                continue

            if len(self.used_sources_from_cmt[source_cmt]) >= self.limit:
                continue

            self.used_sources_from_cmt[source_cmt].add(source)
            return source

        return None


def print_bufhce(name, net):
    print(
        """
(* KEEP, DONT_TOUCH, LOC="{site}" *)
BUFHCE {site} (
.I({clock})
);""".format(site=name, clock=net))


def main():
    """
    GTP_COMMON_MID has clock pips from:

    2 IBUFDS_GTE2 sites (within the GTP_CMMON tile)
    4 GTP_CHANNEL sites within the same column. Each GTP_CHANNEL can provide 2 clocks
    14 clocks lines from the HROW spine
    """

    cmt_clock_sources = ClockSources()
    gtp_channel_clock_sources = ClockSources()
    ibufds_clock_sources = ClockSources()
    site_to_cmt = dict(read_site_to_cmt())
    clock_region_limit = dict()
    clock_region_serdes_location = dict()

    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    def gen_sites(desired_site_type):
        for tile_name in sorted(grid.tiles()):
            loc = grid.loc_of_tilename(tile_name)
            gridinfo = grid.gridinfo_at_loc(loc)
            for site, site_type in gridinfo.sites.items():
                if site_type == desired_site_type:
                    yield tile_name, site

    clock_region_sites = set()

    def get_clock_region_site(site_type, clk_reg):
        for site_name, reg in site_to_cmt.items():
            if site_name.startswith(site_type) and reg in clk_reg:
                if site_name not in clock_region_sites:
                    clock_region_sites.add(site_name)
                    return site_name

    cmt_with_gtp = set()
    for tile_name, site in gen_sites('GTPE2_COMMON'):
        cmt_with_gtp.add(site_to_cmt[site])

    ibufds_inputs = dict()
    input_wires = list()
    for _, site in gen_sites('IBUFDS_GTE2'):
        if site_to_cmt[site] not in cmt_with_gtp:
            continue

        ibufds_i = "{}_ibufds_i".format(site)
        ibufds_ib = "{}_ibufds_ib".format(site)
        ibufds_inputs[site] = [ibufds_i, ibufds_ib]

        input_wires.append("input wire {}".format(ibufds_i))
        input_wires.append("input wire {}".format(ibufds_ib))

    print(
        '''
module top(
    {}
);
    (* KEEP, DONT_TOUCH *)
    LUT6 dummy();
    '''.format(",\n\t".join(input_wires)))

    for _, site in gen_sites('MMCME2_ADV'):
        if site_to_cmt[site] not in cmt_with_gtp:
            continue

        mmcm_clocks = [
            'mmcm_clock_{site}_{idx}'.format(site=site, idx=idx)
            for idx in range(7)
        ]

        for clk in mmcm_clocks:
            cmt_clock_sources.add_clock_source(clk, site_to_cmt[site])

        print(
            """
    wire cin1_{site}, cin2_{site}, {c0}, {c1}, {c2}, {c3}, {c4}, {c5};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    MMCME2_ADV pll_{site} (
        .CLKIN1(cin1_{site}),
        .CLKIN2(cin2_{site}),
        .CLKOUT0({c0}),
        .CLKOUT1({c1}),
        .CLKOUT2({c2}),
        .CLKOUT3({c3}),
        .CLKOUT4({c4}),
        .CLKOUT5({c5}),
        .CLKOUT6({c6})
    );""".format(
                site=site,
                c0=mmcm_clocks[0],
                c1=mmcm_clocks[1],
                c2=mmcm_clocks[2],
                c3=mmcm_clocks[3],
                c4=mmcm_clocks[4],
                c5=mmcm_clocks[5],
                c6=mmcm_clocks[6]))

    for _, site in gen_sites('PLLE2_ADV'):
        if site_to_cmt[site] not in cmt_with_gtp:
            continue

        pll_clocks = [
            'pll_clock_{site}_{idx}'.format(site=site, idx=idx)
            for idx in range(7)
        ]

        for clk in pll_clocks:
            cmt_clock_sources.add_clock_source(clk, site_to_cmt[site])

        print(
            """
    wire cin1_{site}, cin2_{site}, clkfbin_{site}, {c0}, {c1}, {c2}, {c3}, {c4}, {c5}, {c6};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    PLLE2_ADV pll_{site} (
        .CLKIN1(cin1_{site}),
        .CLKIN2(cin2_{site}),
        .CLKFBIN(clkfbin_{site}),
        .CLKOUT0({c0}),
        .CLKOUT1({c1}),
        .CLKOUT2({c2}),
        .CLKOUT3({c3}),
        .CLKOUT4({c4}),
        .CLKOUT5({c5}),
        .CLKFBOUT({c6})
    );""".format(
                site=site,
                c0=pll_clocks[0],
                c1=pll_clocks[1],
                c2=pll_clocks[2],
                c3=pll_clocks[3],
                c4=pll_clocks[4],
                c5=pll_clocks[5],
                c6=pll_clocks[6],
            ))

    for tile, site in gen_sites('IBUFDS_GTE2'):
        if site_to_cmt[site] not in cmt_with_gtp:
            continue

        ibufds_clock = 'ibufds_clock_{site}'.format(site=site)

        ibufds_clock_sources.add_clock_source(ibufds_clock, site_to_cmt[site])

        out_port = "O" if random.random() < 0.5 else "ODIV2"
        i_port = ibufds_inputs[site][0]
        ib_port = ibufds_inputs[site][1]

        print(
            """
    wire {o};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    IBUFDS_GTE2 ibufds_{site} (
        .I({i}),
        .IB({ib}),
        .{out_port}({o})
    );""".format(
                site=site,
                i=i_port,
                ib=ib_port,
                o=ibufds_clock,
                out_port=out_port))

    for _, site in gen_sites('GTPE2_CHANNEL'):
        if site_to_cmt[site] not in cmt_with_gtp:
            continue

        gtp_channel_clock_rx = 'gtp_channel_clock_{site}_rxclkout'.format(
            site=site)
        gtp_channel_clock_tx = 'gtp_channel_clock_{site}_txclkout'.format(
            site=site)

        gtp_channel_clock_sources.add_clock_source(
            gtp_channel_clock_rx, site_to_cmt[site])
        gtp_channel_clock_sources.add_clock_source(
            gtp_channel_clock_tx, site_to_cmt[site])

        print(
            """
    wire {rx}, {tx};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    GTPE2_CHANNEL gtp_channel_{site} (
        .RXOUTCLK({rx}),
        .TXOUTCLK({tx})
    );""".format(site=site, rx=gtp_channel_clock_rx, tx=gtp_channel_clock_tx))

    for cmt in cmt_with_gtp:
        cmt_clock_used = False

        for _, bufhce in gen_sites('BUFHCE'):
            if site_to_cmt[bufhce] != cmt:
                continue

            chance = random.random()

            use_gtp_channel, use_ibufds, use_cmt = todo_pips()

            if (chance < 0.2 and use_cmt) or not cmt_clock_used:
                # There must always be at least one CMT clock used
                # to trigger the bits for the GTP_COMMON and IBUFDS pips
                cmt_clock_used = True
                clock_name = cmt_clock_sources.get_random_source(cmt)
            elif chance > 0.2 and chance < 0.4 and use_ibufds:
                clock_name = ibufds_clock_sources.get_random_source(cmt)
            elif chance < 0.7 and use_gtp_channel:
                clock_name = gtp_channel_clock_sources.get_random_source(cmt)
            else:
                continue

            if clock_name is None:
                continue

            print_bufhce("{}".format(bufhce), clock_name)

    print('endmodule')


if __name__ == "__main__":
    main()
