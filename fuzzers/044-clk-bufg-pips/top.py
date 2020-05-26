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
""" Emits top.v's for various BUFHCE routing inputs. """
import os
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray.lut_maker import LutMaker
from prjxray.db import Database
from io import StringIO

CMT_XY_FUN = util.create_xy_fun(prefix='')
BUFGCTRL_XY_FUN = util.create_xy_fun('BUFGCTRL_')


def read_site_to_cmt():
    """ Yields clock sources and which CMT they route within. """
    with open(os.path.join(os.getenv('FUZDIR'), 'build',
                           'cmt_regions.csv')) as f:
        for l in f:
            site, cmt = l.strip().split(',')
            yield (site, cmt)


class ClockSources(object):
    """ Class for tracking clock sources.

    Some clock sources can be routed to any CMT, for these, cmt='ANY'.
    For clock sources that belong to a CMT, cmt should be set to the CMT of
    the source.

    """

    def __init__(self):
        self.sources = {}
        self.merged_sources = {}
        self.source_to_cmt = {}
        self.used_sources_from_cmt = {}

    def add_clock_source(self, source, cmt):
        """ Adds a source from a specific CMT.

        cmt='ANY' indicates that this source can be routed to any CMT.
        """
        if cmt not in self.sources:
            self.sources[cmt] = []

        self.sources[cmt].append(source)
        assert source not in self.source_to_cmt or self.source_to_cmt[
            source] == cmt, source
        self.source_to_cmt[source] = cmt

    def get_random_source(self, cmt):
        """ Get a random source that is routable to the specific CMT.

        get_random_source will return a source that is either cmt='ANY',
        cmt equal to the input CMT, or the adjecent CMT.

        """
        if cmt not in self.merged_sources:
            choices = []
            if 'ANY' in self.sources:
                choices.extend(self.sources['ANY'])

            if cmt in self.sources:
                choices.extend(self.sources[cmt])

            x, y = CMT_XY_FUN(cmt)

            if x % 2 == 0:
                x += 1
            else:
                x -= 1

            paired_cmt = 'X{}Y{}'.format(x, y)

            if paired_cmt in self.sources:
                choices.extend(self.sources[paired_cmt])

            self.merged_sources[cmt] = choices

        if self.merged_sources[cmt]:
            source = random.choice(self.merged_sources[cmt])

            source_cmt = self.source_to_cmt[source]
            if source_cmt not in self.used_sources_from_cmt:
                self.used_sources_from_cmt[source_cmt] = set()

            self.used_sources_from_cmt[source_cmt].add(source)

            if source_cmt != 'ANY' and len(
                    self.used_sources_from_cmt[source_cmt]) > 14:
                print('//', self.used_sources_from_cmt)
                self.used_sources_from_cmt[source_cmt].remove(source)
                return None
            else:
                return source


def main():
    """
    BUFG's can be driven from:

        Interconnect
        HROW cascade

    """

    print(
        '''
module top();
    (* KEEP, DONT_TOUCH *)
    LUT6 dummy();
    ''')

    site_to_cmt = dict(read_site_to_cmt())
    luts = LutMaker()
    wires = StringIO()
    bufgs = StringIO()

    clock_sources = ClockSources()

    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    def gen_sites(desired_site_type):
        for tile_name in sorted(grid.tiles()):
            loc = grid.loc_of_tilename(tile_name)
            gridinfo = grid.gridinfo_at_loc(loc)
            for site, site_type in gridinfo.sites.items():
                if site_type == desired_site_type:
                    yield tile_name, site

    for _, site in gen_sites('MMCME2_ADV'):
        mmcm_clocks = [
            'mmcm_clock_{site}_{idx}'.format(site=site, idx=idx)
            for idx in range(13)
        ]

        for clk in mmcm_clocks:
            clock_sources.add_clock_source(clk, site_to_cmt[site])

        print(
            """
    wire {c0}, {c1}, {c2}, {c3}, {c4}, {c5};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    MMCME2_ADV pll_{site} (
        .CLKOUT0({c0}),
        .CLKOUT0B({c1}),
        .CLKOUT1({c2}),
        .CLKOUT1B({c3}),
        .CLKOUT2({c4}),
        .CLKOUT2B({c5}),
        .CLKOUT3({c6}),
        .CLKOUT3B({c7}),
        .CLKOUT4({c8}),
        .CLKOUT5({c9}),
        .CLKOUT6({c10}),
        .CLKFBOUT({c11}),
        .CLKFBOUTB({c12})
    );
        """.format(
                site=site,
                c0=mmcm_clocks[0],
                c1=mmcm_clocks[1],
                c2=mmcm_clocks[2],
                c3=mmcm_clocks[3],
                c4=mmcm_clocks[4],
                c5=mmcm_clocks[5],
                c6=mmcm_clocks[6],
                c7=mmcm_clocks[7],
                c8=mmcm_clocks[8],
                c9=mmcm_clocks[9],
                c10=mmcm_clocks[10],
                c11=mmcm_clocks[11],
                c12=mmcm_clocks[12],
            ))

    for _, site in sorted(gen_sites("BUFGCTRL"),
                          key=lambda x: BUFGCTRL_XY_FUN(x[1])):
        print(
            """
    wire O_{site};
    wire S1_{site};
    wire S0_{site};
    wire IGNORE1_{site};
    wire IGNORE0_{site};
    wire I1_{site};
    wire I0_{site};
    wire CE1_{site};
    wire CE0_{site};
    """.format(site=site),
            file=wires)

        print(
            """
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    BUFGCTRL bufg_{site} (
        .O(O_{site}),
        .S1(S1_{site}),
        .S0(S0_{site}),
        .IGNORE1(IGNORE1_{site}),
        .IGNORE0(IGNORE0_{site}),
        .I1(I1_{site}),
        .I0(I0_{site}),
        .CE1(CE1_{site}),
        .CE0(CE0_{site})
        );
        """.format(site=site),
            file=bufgs)
    """ BUFG clock sources:

    2 from interconnect
    Output of BUFG +/- 1
    Cascade in (e.g. PLL, MMCM)

    """

    CLOCK_CHOICES = (
        'LUT',
        'BUFG_+1',
        'BUFG_-1',
        'CASCADE',
    )

    def find_bufg_cmt(tile):
        if '_BOT_' in tile:
            inc = 1
        else:
            inc = -1

        loc = grid.loc_of_tilename(tile)

        offset = 1

        while True:
            gridinfo = grid.gridinfo_at_loc(
                (loc.grid_x, loc.grid_y + offset * inc))
            if gridinfo.tile_type.startswith('CLK_HROW_'):
                return site_to_cmt[list(gridinfo.sites.keys())[0]]

            offset += 1

    def get_clock_net(tile, site, source_type):
        if source_type == 'LUT':
            return luts.get_next_output_net()
        elif source_type == 'BUFG_+1':
            x, y = BUFGCTRL_XY_FUN(site)

            target_y = y + 1
            max_y = ((y // 16) + 1) * 16

            if target_y >= max_y:
                target_y -= 16

            return 'O_BUFGCTRL_X{x}Y{y}'.format(x=x, y=target_y)
        elif source_type == 'BUFG_-1':
            x, y = BUFGCTRL_XY_FUN(site)

            target_y = y - 1
            min_y = (y // 16) * 16

            if target_y < min_y:
                target_y += 16

            return 'O_BUFGCTRL_X{x}Y{y}'.format(x=x, y=target_y)
        elif source_type == 'CASCADE':
            cmt = find_bufg_cmt(tile)
            return clock_sources.get_random_source(cmt)
        else:
            assert False, source_type

    for tile, site in sorted(gen_sites("BUFGCTRL"),
                             key=lambda x: BUFGCTRL_XY_FUN(x[1])):
        if random.randint(0, 1):
            print(
                """
    assign I0_{site} = {i0_net};""".format(
                    site=site,
                    i0_net=get_clock_net(
                        tile, site, random.choice(CLOCK_CHOICES))),
                file=bufgs)

        if random.randint(0, 1):
            print(
                """
    assign I1_{site} = {i1_net};""".format(
                    site=site,
                    i1_net=get_clock_net(
                        tile, site, random.choice(CLOCK_CHOICES))),
                file=bufgs)

        print(
            """
    assign S0_{site} = {s0_net};
    assign S1_{site} = {s1_net};
    assign IGNORE0_{site} = {ignore0_net};
    assign IGNORE1_{site} = {ignore1_net};
    assign CE0_{site} = {ce0_net};
    assign CE1_{site} = {ce1_net};
        """.format(
                site=site,
                s0_net=luts.get_next_output_net(),
                s1_net=luts.get_next_output_net(),
                ignore0_net=luts.get_next_output_net(),
                ignore1_net=luts.get_next_output_net(),
                ce0_net=luts.get_next_output_net(),
                ce1_net=luts.get_next_output_net(),
            ),
            file=bufgs)

    for l in luts.create_wires_and_luts():
        print(l)

    print(wires.getvalue())
    print(bufgs.getvalue())

    itr = iter(gen_sites('BUFHCE'))

    for tile, site in sorted(gen_sites("BUFGCTRL"),
                             key=lambda x: BUFGCTRL_XY_FUN(x[1])):
        if random.randint(0, 1):
            _, bufhce_site = next(itr)

            print(
                """
    (* KEEP, DONT_TOUCH, LOC = "{bufhce_site}" *)
    BUFHCE bufhce_{bufhce_site} (
        .I(O_{site})
        );""".format(
                    site=site,
                    bufhce_site=bufhce_site,
                ))

    print("endmodule")


if __name__ == '__main__':
    main()
