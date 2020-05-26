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
import re
from prjxray import util
from prjxray.lut_maker import LutMaker
from prjxray.db import Database
from io import StringIO

CMT_XY_FUN = util.create_xy_fun(prefix='')


def read_site_to_cmt():
    """ Yields clock sources and which CMT they route within. """
    with open(os.path.join(os.getenv('FUZDIR'), 'build',
                           'cmt_regions.csv')) as f:
        for l in f:
            site, cmt, tile = l.strip().split(',')
            yield (tile, site, cmt)


def make_ccio_route_options():

    # Read the PIP lists
    piplist_path = os.path.join(
        os.getenv("FUZDIR"), "..", "piplist", "build", "hclk_cmt")

    pips = []
    for fname in os.listdir(piplist_path):
        if not fname.endswith(".txt"):
            continue

        fullname = os.path.join(piplist_path, fname)
        with open(fullname, "r") as fp:
            pips += [l.strip() for l in fp.readlines()]

    # Get PIPs that mention FREQ_REFn wires. These are the ones that we want
    # force routing through.
    pips = [p for p in pips if "FREQ_REF" in p]

    # Sort by tile type
    options = {}
    for pip in pips:
        tile, dst, src = pip.split(".")

        for a, b in ((src, dst), (dst, src)):
            match = re.match(r".*FREQ_REF([0-3]).*", a)
            if match is not None:
                n = int(match.group(1))

                if tile not in options:
                    options[tile] = {}
                if n not in options[tile]:
                    options[tile][n] = set()

                options[tile][n].add(b)

    return options


class ClockSources(object):
    """ Class for tracking clock sources.

    Some clock sources can be routed to any CMT, for these, cmt='ANY'.
    For clock sources that belong to a CMT, cmt should be set to the CMT of
    the source.

    """

    def __init__(self):
        self.sources = {}
        self.source_to_cmt = {}
        self.used_sources_from_cmt = {}

    def add_clock_source(self, source, cmt):
        """ Adds a source from a specific CMT.

        cmt='ANY' indicates that this source can be routed to any CMT.
        """
        if cmt not in self.sources:
            self.sources[cmt] = []

        self.sources[cmt].append(source)
        self.source_to_cmt[source] = cmt

    def remove_clock_source(self, source, cmt="ANY"):
        """
        Removes a clock source from the available clock sources list
        """
        if source in self.source_to_cmt:
            del self.source_to_cmt[source]

        if cmt == "ANY":
            for sources in self.sources.values():
                if source in sources:
                    sources.remove(source)
        else:
            if source in self.sources[cmt]:
                self.sources[cmt].remove(source)

    def get_random_source(
            self, cmt, uses_left_right_routing=False, no_repeats=False):
        """ Get a random source that is routable to the specific CMT.

        get_random_source will return a source that is either cmt='ANY',
        cmt equal to the input CMT, or the adjecent CMT.

        """

        choices = []

        if cmt in self.sources:
            choices.extend(self.sources[cmt])

        if uses_left_right_routing:
            x, y = CMT_XY_FUN(cmt)

            if x % 2 == 0:
                x += 1
            else:
                x -= 1

            paired_cmt = 'X{}Y{}'.format(x, y)

            if paired_cmt in self.sources:
                for source in self.sources[paired_cmt]:
                    if 'BUFHCE' not in source:
                        choices.append(source)

        random.shuffle(choices)

        if not uses_left_right_routing:
            return choices[0]

        for source in choices:

            source_cmt = self.source_to_cmt[source]

            if source_cmt not in self.used_sources_from_cmt:
                self.used_sources_from_cmt[source_cmt] = set()

            if no_repeats and source in self.used_sources_from_cmt[source_cmt]:
                continue

            if len(self.used_sources_from_cmt[source_cmt]) >= 14:
                continue

            self.used_sources_from_cmt[source_cmt].add(source)

            return source

        return None


def get_paired_iobs(db, grid, tile_name):
    """ The two IOB33M's above and below the HCLK row have dedicate clock lines.
    """

    gridinfo = grid.gridinfo_at_tilename(tile_name)
    loc = grid.loc_of_tilename(tile_name)

    if gridinfo.tile_type.endswith('_L'):
        inc = 1
        lr = 'R'
    else:
        inc = -1
        lr = 'L'

    idx = 1
    while True:
        gridinfo = grid.gridinfo_at_loc((loc.grid_x + inc * idx, loc.grid_y))

        if gridinfo.tile_type.startswith('HCLK_IOI'):
            break

        idx += 1

    # A map of y deltas to CCIO wire indices
    CCIO_INDEX = {-1: 0, -3: 1, +2: 3, +4: 2}

    # Move from HCLK_IOI column to IOB column
    idx += 1

    for dy in [-1, -3, 2, 4]:
        iob_loc = (loc.grid_x + inc * idx, loc.grid_y + dy)
        gridinfo = grid.gridinfo_at_loc(iob_loc)
        tile_name = grid.tilename_at_loc(iob_loc)

        assert gridinfo.tile_type.startswith(lr + 'IOB'), (
            gridinfo, lr + 'IOB')

        for site, site_type in gridinfo.sites.items():
            if site_type in ['IOB33M', 'IOB18M']:
                yield tile_name, site, site_type[-3:-1], CCIO_INDEX[dy]


def check_allowed(mmcm_pll_dir, cmt):
    """ Check whether the CMT specified is in the allowed direction.

    This function is designed to bias sources to either the left or right
    input lines.

    """
    if mmcm_pll_dir == 'BOTH':
        return True
    elif mmcm_pll_dir == 'ODD':
        x, y = CMT_XY_FUN(cmt)
        return (x & 1) == 1
    elif mmcm_pll_dir == 'EVEN':
        x, y = CMT_XY_FUN(cmt)
        return (x & 1) == 0
    else:
        assert False, mmcm_pll_dir


def main():
    """
    HCLK_CMT switch box has the follow inputs:

    4 IOBs above and below
    14 MMCM outputs
    8 PLL outputs
    4 PHASER_IN outputs
    2 INT connections

    and the following outputs:

    3 PLLE2 inputs
    2 BUFMR inputs
    3 MMCM inputs
    ~2 MMCM -> BUFR???
    """

    clock_sources = ClockSources()
    adv_clock_sources = ClockSources()

    tile_site_cmt = list(read_site_to_cmt())
    site_to_cmt = {tsc[1]: tsc[2] for tsc in tile_site_cmt}
    cmt_to_hclk = {
        tsc[2]: tsc[0]
        for tsc in tile_site_cmt
        if tsc[0].startswith("HCLK_CMT_")
    }

    ccio_route_options = make_ccio_route_options()

    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    def gen_sites(desired_site_type):
        for tile_name in sorted(grid.tiles()):
            loc = grid.loc_of_tilename(tile_name)
            gridinfo = grid.gridinfo_at_loc(loc)
            for site, site_type in gridinfo.sites.items():
                if site_type == desired_site_type:
                    yield tile_name, site

    hclk_cmts = set()
    ins = []
    iobs = StringIO()

    hclk_cmt_tiles = set()
    for tile_name, site in gen_sites('BUFMRCE'):
        cmt = site_to_cmt[site]
        hclk_cmts.add(cmt)
        hclk_cmt_tiles.add(tile_name)

    mmcm_pll_only = random.randint(0, 1)
    mmcm_pll_dir = random.choice(('ODD', 'EVEN', 'BOTH'))

    print(
        '// mmcm_pll_only {} mmcm_pll_dir {}'.format(
            mmcm_pll_only, mmcm_pll_dir))

    have_iob_clocks = random.random() > .1

    iob_to_hclk = {}
    iob_clks = {}
    for tile_name in sorted(hclk_cmt_tiles):
        for _, site, volt, ccio in get_paired_iobs(db, grid, tile_name):
            iob_clock = 'clock_IBUF_{site}'.format(site=site)

            iob_to_hclk[site] = (tile_name, ccio)
            cmt = site_to_cmt[site]

            if cmt not in iob_clks:
                iob_clks[cmt] = ['']

            iob_clks[cmt].append(iob_clock)

            ins.append('input clk_{site}'.format(site=site))

            if have_iob_clocks:
                if check_allowed(mmcm_pll_dir, cmt):
                    clock_sources.add_clock_source(iob_clock, cmt)
                adv_clock_sources.add_clock_source(iob_clock, cmt)

            print(
                """
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    wire clock_IBUF_{site};
    IBUF #( .IOSTANDARD("LVCMOS{volt}") ) ibuf_{site} (
        .I(clk_{site}),
        .O(clock_IBUF_{site})
        );
                    """.format(volt=volt, site=site),
                file=iobs)

    print(
        '''
module top({inputs});
    (* KEEP, DONT_TOUCH *)
    LUT6 dummy();
    '''.format(inputs=', '.join(ins)))

    print(iobs.getvalue())

    luts = LutMaker()
    wires = StringIO()
    bufhs = StringIO()

    for _, site in gen_sites('MMCME2_ADV'):
        mmcm_clocks = [
            'mmcm_clock_{site}_{idx}'.format(site=site, idx=idx)
            for idx in range(13)
        ]

        if check_allowed(mmcm_pll_dir, site_to_cmt[site]):
            for clk in mmcm_clocks:
                clock_sources.add_clock_source(clk, site_to_cmt[site])

        print(
            """
    wire cin1_{site}, cin2_{site}, clkfbin_{site}, {c0}, {c1}, {c2}, {c3}, {c4}, {c5};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    MMCME2_ADV pll_{site} (
        .CLKIN1(cin1_{site}),
        .CLKIN2(cin2_{site}),
        .CLKFBIN(clkfbin_{site}),
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

    for _, site in gen_sites('PLLE2_ADV'):
        pll_clocks = [
            'pll_clock_{site}_{idx}'.format(site=site, idx=idx)
            for idx in range(7)
        ]

        if check_allowed(mmcm_pll_dir, site_to_cmt[site]):
            for clk in pll_clocks:
                clock_sources.add_clock_source(clk, site_to_cmt[site])

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
    );
        """.format(
                site=site,
                c0=pll_clocks[0],
                c1=pll_clocks[1],
                c2=pll_clocks[2],
                c3=pll_clocks[3],
                c4=pll_clocks[4],
                c5=pll_clocks[5],
                c6=pll_clocks[6],
            ))

    for tile_name, site in gen_sites('BUFHCE'):
        print(
            """
    wire I_{site};
    wire O_{site};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    BUFHCE buf_{site} (
        .I(I_{site}),
        .O(O_{site})
    );
                    """.format(site=site, ),
            file=bufhs)

        if site_to_cmt[site] in hclk_cmts:
            if not mmcm_pll_only:
                clock_sources.add_clock_source(
                    'O_{site}'.format(site=site), site_to_cmt[site])
            adv_clock_sources.add_clock_source(
                'O_{site}'.format(site=site), site_to_cmt[site])

    hclks_used_by_cmt = {}
    for cmt in site_to_cmt.values():
        hclks_used_by_cmt[cmt] = set()

    def check_hclk_src(src, src_cmt):
        if len(hclks_used_by_cmt[src_cmt]
               ) >= 12 and src not in hclks_used_by_cmt[src_cmt]:
            return None
        else:
            hclks_used_by_cmt[src_cmt].add(src)
            return src

    # Track used IOB sources
    used_iob_clks = set()

    if random.random() > .10:
        for tile_name, site in gen_sites('BUFHCE'):

            wire_name = clock_sources.get_random_source(
                site_to_cmt[site],
                uses_left_right_routing=True,
                no_repeats=mmcm_pll_only)

            if wire_name is not None and 'BUFHCE' in wire_name:
                # Looping a BUFHCE to a BUFHCE requires using a hclk in the
                # CMT of the source
                src_cmt = clock_sources.source_to_cmt[wire_name]

                wire_name = check_hclk_src(wire_name, src_cmt)

            if wire_name is None:
                continue

            if "IBUF" in wire_name:
                used_iob_clks.add(wire_name)
                clock_sources.remove_clock_source(wire_name)
                adv_clock_sources.remove_clock_source(wire_name)

            print(
                """
        assign I_{site} = {wire_name};""".format(
                    site=site,
                    wire_name=wire_name,
                ),
                file=bufhs)

    for tile_name, site in gen_sites('BUFMRCE'):
        pass

    for l in luts.create_wires_and_luts():
        print(l)

    print(wires.getvalue())
    print(bufhs.getvalue())

    for _, site in gen_sites('BUFR'):

        # Do not use BUFR always
        if random.random() < 0.50:
            continue

        available_srcs = set(iob_clks[site_to_cmt[site]]) - used_iob_clks
        if len(available_srcs) == 0:
            continue

        src = random.choice(list(available_srcs))

        if src != "":
            used_iob_clks.add(src)
            clock_sources.remove_clock_source(src)
            adv_clock_sources.remove_clock_source(src)

        adv_clock_sources.add_clock_source(
            'O_{site}'.format(site=site), site_to_cmt[site])

        print(
            """
    wire O_{site};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    BUFR bufr_{site} (
        .I({I}),
        .O(O_{site})
        );""".format(I=src, site=site))

    route_file = open("routes.txt", "w")

    def fix_ccio_route(net):

        # Get the IOB site name
        match = re.match(r".*_IBUF_(.*)", net)
        assert match is not None, net
        iob_site = match.group(1)

        # Get associated HCLK_CMT tile and CCIO wire index
        hclk_tile_name, ccio = iob_to_hclk[iob_site]

        # Get HCLK_CMT tile type
        hclk_tile = hclk_tile_name.rsplit("_", maxsplit=1)[0]

        # Pick a random route option
        opts = list(ccio_route_options[hclk_tile][ccio])
        route = random.choice(opts)
        route = "{}/{}".format(hclk_tile_name, route)
        route_file.write("{} {}\n".format(net, route))

    for _, site in gen_sites('PLLE2_ADV'):
        for cin in ('cin1', 'cin2', 'clkfbin'):
            if random.random() > .2:

                src = adv_clock_sources.get_random_source(site_to_cmt[site])

                src_cmt = adv_clock_sources.source_to_cmt[src]

                if 'IBUF' not in src and 'BUFR' not in src:
                    # Clocks from input pins do not require HCLK's, all other
                    # sources route from a global row clock.
                    src = check_hclk_src(src, src_cmt)

                if src is None:
                    continue

                if "IBUF" in src:
                    clock_sources.remove_clock_source(src)
                    adv_clock_sources.remove_clock_source(src)
                    fix_ccio_route(src)

                print(
                    """
        assign {cin}_{site} = {csrc};
            """.format(cin=cin, site=site, csrc=src))

    for _, site in gen_sites('MMCME2_ADV'):
        for cin in ('cin1', 'cin2', 'clkfbin'):
            if random.random() > .2:

                src = adv_clock_sources.get_random_source(site_to_cmt[site])

                src_cmt = adv_clock_sources.source_to_cmt[src]
                if 'IBUF' not in src and 'BUFR' not in src:
                    # Clocks from input pins do not require HCLK's, all other
                    # sources route from a global row clock.
                    src = check_hclk_src(src, src_cmt)

                if src is None:
                    continue

                if "IBUF" in src:
                    clock_sources.remove_clock_source(src)
                    adv_clock_sources.remove_clock_source(src)
                    fix_ccio_route(src)

                print(
                    """
        assign {cin}_{site} = {csrc};
            """.format(cin=cin, site=site, csrc=src))

    print("endmodule")


if __name__ == '__main__':
    main()
