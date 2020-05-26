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
import re
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import verilog
from prjxray.grid_types import GridLoc
from prjxray.db import Database
from prjxray.lut_maker import LutMaker
from io import StringIO
import csv
import sys

CMT_XY_FUN = util.create_xy_fun(prefix='')
BUFGCTRL_XY_FUN = util.create_xy_fun('BUFGCTRL_')
BUFHCE_XY_FUN = util.create_xy_fun('BUFHCE_')


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def gen_sites(desired_site_type):
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        for site, site_type in gridinfo.sites.items():
            if site_type == desired_site_type:
                yield loc, gridinfo.tile_type, site


def gen_bufhce_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        sites = []

        for site, site_type in gridinfo.sites.items():
            if site_type == 'BUFHCE':
                sites.append(site)

        if sites:
            yield tile_name, sorted(sites)


def get_cmt_loc(cmt_tile_name):
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    return grid.loc_of_tilename(cmt_tile_name)


def read_site_to_cmt():
    """ Yields clock sources and which CMT they route within. """
    with open(os.path.join(os.getenv('FUZDIR'), 'build',
                           'cmt_regions.csv')) as f:
        for l in f:
            site, cmt = l.strip().split(',')
            yield (site, cmt)


def read_pss_clocks():
    with open(os.path.join(os.getenv('FUZDIR'), 'build',
                           'pss_clocks.csv')) as f:
        for l in csv.DictReader(f):
            yield l


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
        self.sources_by_loc = {}
        self.active_cmt_ports = {}

    def add_clock_source(self, source, cmt, loc=None):
        """ Adds a source from a specific CMT.

        cmt='ANY' indicates that this source can be routed to any CMT.
        """
        if cmt not in self.sources:
            self.sources[cmt] = []

        self.sources[cmt].append(source)
        assert source not in self.source_to_cmt or self.source_to_cmt[
            source] == cmt, source
        self.source_to_cmt[source] = cmt

        self.add_bufg_clock_source(source, cmt, loc)

    def add_bufg_clock_source(self, source, cmt, loc):
        if loc not in self.sources_by_loc:
            self.sources_by_loc[loc] = []

        self.sources_by_loc[loc].append((cmt, source))

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
                self.used_sources_from_cmt[source_cmt].remove(source)
                return None
            else:
                return source

    def get_bufg_source(self, loc, tile_type, site, todos, i_wire, used_only):
        bufg_sources = []

        top = '_TOP_' in tile_type
        bottom = '_BOT_' in tile_type

        assert top ^ bottom, tile_type

        if top:
            for src_loc, cmt_sources in self.sources_by_loc.items():
                if src_loc is None:
                    continue
                if src_loc.grid_y <= loc.grid_y:
                    bufg_sources.extend(cmt_sources)
        elif bottom:
            for src_loc, cmt_sources in self.sources_by_loc.items():
                if src_loc is None:
                    continue
                if src_loc.grid_y > loc.grid_y:
                    bufg_sources.extend(cmt_sources)

        # CLK_HROW_TOP_R_CK_BUFG_CASCO0  -> CLK_BUFG_BUFGCTRL0_I0
        # CLK_HROW_TOP_R_CK_BUFG_CASCO22 -> CLK_BUFG_BUFGCTRL11_I0
        # CLK_HROW_TOP_R_CK_BUFG_CASCO23 -> CLK_BUFG_BUFGCTRL11_I1
        # CLK_HROW_BOT_R_CK_BUFG_CASCO27 -> CLK_BUFG_BUFGCTRL13_I1

        x, y = BUFGCTRL_XY_FUN(site)
        assert x == 0
        y = y % 16

        assert i_wire in [0, 1], i_wire

        casco_wire = '{tile_type}_CK_BUFG_CASCO{casco_idx}'.format(
            tile_type=tile_type.replace('BUFG', 'HROW'),
            casco_idx=(y * 2 + i_wire))

        if casco_wire not in todos:
            return None

        target_wires = []

        need_bufr = False
        for src_wire in todos[casco_wire]:
            if 'BUFRCLK' in src_wire:
                need_bufr = True
                break

        for cmt, wire in bufg_sources:
            if 'BUFR' in wire:
                if need_bufr:
                    target_wires.append((cmt, wire))
            else:
                target_wires.append((cmt, wire))

        random.shuffle(target_wires)
        for cmt, source in target_wires:
            if cmt == 'ANY':
                return source
            else:
                # Make sure to not try to import move than 14 sources from
                # the CMT, there is limited routing.
                if cmt not in self.used_sources_from_cmt:
                    self.used_sources_from_cmt[cmt] = set()

                if source in self.used_sources_from_cmt[cmt]:
                    return source
                elif used_only:
                    continue

                if len(self.used_sources_from_cmt[cmt]) < 14:
                    self.used_sources_from_cmt[cmt].add(source)
                    return source
                else:
                    continue

        return None


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
    elif mmcm_pll_dir == 'NONE':
        return False
    else:
        assert False, mmcm_pll_dir


def read_todo():
    dsts = {}

    with open(os.path.join('..', 'todo_all.txt')) as f:
        for l in f:
            tile_type, dst, src = l.strip().split('.')

            if dst not in dsts:
                dsts[dst] = set()

            dsts[dst].add(src)

    return dsts


def need_int_connections(todos):
    for srcs in todos.values():
        for src in srcs:
            if re.search('INT_._.', src):
                return True

    return False


def bufhce_in_todo(todos, site):
    if 'BUFHCE' in site:
        # CLK_HROW_CK_MUX_OUT_R9 -> X1Y9
        # CLK_HROW_CK_MUX_OUT_L11 -> X0Y35
        x, y = BUFHCE_XY_FUN(site)
        y = y % 12

        if x == 0:
            lr = 'L'
        elif x == 1:
            lr = 'R'
        else:
            assert False, x

        return 'CLK_HROW_CK_MUX_OUT_{lr}{y}'.format(lr=lr, y=y) in todos
    else:
        return True


def need_gclk_connection(todos, site):
    x, y = BUFGCTRL_XY_FUN(site)
    assert x == 0

    src_wire = 'CLK_HROW_R_CK_GCLK{}'.format(y)
    for srcs in todos.values():
        if src_wire in srcs:
            return True

    return False


def only_gclk_left(todos):
    for srcs in todos.values():
        for src in srcs:
            if 'GCLK' not in src:
                return False

    return True


def main():
    """
    BUFHCE's can be driven from:

        MMCME2_ADV
        PLLE2_ADV
        BUFGCTRL
        Local INT connect
        PS7 (Zynq)
    """

    print('''
// SEED={}
module top();
    '''.format(os.getenv('SEED')))

    is_zynq = os.getenv('XRAY_DATABASE') == 'zynq7'
    clock_sources = ClockSources()

    site_to_cmt = dict(read_site_to_cmt())

    if is_zynq:
        pss_clocks = list(read_pss_clocks())

    # To ensure that all left or right sources are used, sometimes only MMCM/PLL
    # sources are allowed.  The force of ODD/EVEN/BOTH further biases the
    # clock sources to the left or right column inputs.
    mmcm_pll_only = random.randint(0, 1)
    mmcm_pll_dir = random.choice(('ODD', 'EVEN', 'BOTH', 'NONE'))

    todos = read_todo()

    if only_gclk_left(todos):
        mmcm_pll_dir = 'NONE'

    if not mmcm_pll_only:
        if need_int_connections(todos):
            for _ in range(10):
                clock_sources.add_clock_source('one', 'ANY')
                clock_sources.add_clock_source('zero', 'ANY')

    print("""
    wire zero = 0;
    wire one = 1;""")

    for loc, _, site in gen_sites('MMCME2_ADV'):
        mmcm_clocks = [
            'mmcm_clock_{site}_{idx}'.format(site=site, idx=idx)
            for idx in range(13)
        ]

        if check_allowed(mmcm_pll_dir, site_to_cmt[site]):
            for clk in mmcm_clocks:
                clock_sources.add_clock_source(clk, site_to_cmt[site], loc)

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

    for loc, _, site in gen_sites('PLLE2_ADV'):
        pll_clocks = [
            'pll_clock_{site}_{idx}'.format(site=site, idx=idx)
            for idx in range(6)
        ]

        if check_allowed(mmcm_pll_dir, site_to_cmt[site]):
            for clk in pll_clocks:
                clock_sources.add_clock_source(clk, site_to_cmt[site], loc)

        print(
            """
    wire {c0}, {c1}, {c2}, {c3}, {c4}, {c5};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    PLLE2_ADV pll_{site} (
        .CLKOUT0({c0}),
        .CLKOUT1({c1}),
        .CLKOUT2({c2}),
        .CLKOUT3({c3}),
        .CLKOUT4({c4}),
        .CLKOUT5({c5})
    );
        """.format(
                site=site,
                c0=pll_clocks[0],
                c1=pll_clocks[1],
                c2=pll_clocks[2],
                c3=pll_clocks[3],
                c4=pll_clocks[4],
                c5=pll_clocks[5],
            ))

    for loc, _, site in gen_sites('BUFR'):
        clock_sources.add_bufg_clock_source(
            'O_{site}'.format(site=site), site_to_cmt[site], loc)
        print(
            """
    wire O_{site};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    BUFR bufr_{site} (
        .O(O_{site})
        );""".format(site=site))

    if is_zynq:

        # FCLK clocks. Those are generated by the PS and go directly to one of
        # the CLK_HROW tile.
        clocks = [
            "PSS_FCLKCLK0",
            "PSS_FCLKCLK1",
            "PSS_FCLKCLK2",
            "PSS_FCLKCLK3",
        ]

        loc, _, site = next(gen_sites('PS7'))

        print("")

        # Add clock sources and generate wires
        for wire in clocks:
            clock_info = [d for d in pss_clocks if d["pin"] == wire][0]

            # CMT tile
            cmt_tile = clock_info["tile"]
            cmt_loc = get_cmt_loc(cmt_tile)

            # Add only if the input wire is in the todo list
            dsts = [k for k, v in todos.items() if clock_info["wire"] in v]
            if len(dsts) > 0:

                # Wire source clock region. The PS7 is always left of the
                # CLK_HROW tile, but it does not matter here.
                regions = clock_info["clock_regions"].split()
                regions = sorted([(int(r[1]), int(r[3])) for r in regions])

                # Add the clock source
                cmt = "X{}Y{}".format(regions[0][0], regions[0][1])
                clock_sources.add_clock_source(wire, cmt, cmt_loc)

            print("    wire {};".format(wire))

        print(
            """
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    PS7 ps7_{site} (
        .FCLKCLK({{{fclk3}, {fclk2}, {fclk1}, {fclk0}}})
    );
        """.format(
                site=site,
                fclk0=clocks[0],
                fclk1=clocks[1],
                fclk2=clocks[2],
                fclk3=clocks[3]))

    luts = LutMaker()
    bufhs = StringIO()
    bufgs = StringIO()

    gclks = []
    for _, _, site in sorted(gen_sites("BUFGCTRL"),
                             key=lambda x: BUFGCTRL_XY_FUN(x[2])):
        wire_name = 'gclk_{}'.format(site)
        gclks.append(wire_name)

        include_source = True
        if mmcm_pll_only:
            include_source = False
        elif only_gclk_left(todos):
            include_source = need_gclk_connection(todos, site)

        if include_source:
            clock_sources.add_clock_source(wire_name, 'ANY')

        print("""
    wire {wire_name};
    """.format(wire_name=wire_name))
        print(
            """
    wire I1_{site};
    wire I0_{site};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    BUFGCTRL bufg_{site} (
        .O({wire_name}),
        .S1({s1net}),
        .S0({s0net}),
        .IGNORE1({ignore1net}),
        .IGNORE0({ignore0net}),
        .I1(I1_{site}),
        .I0(I0_{site}),
        .CE1({ce1net}),
        .CE0({ce0net})
        );
        """.format(
                site=site,
                wire_name=wire_name,
                s1net=luts.get_next_output_net(),
                s0net=luts.get_next_output_net(),
                ignore1net=luts.get_next_output_net(),
                ignore0net=luts.get_next_output_net(),
                ce1net=luts.get_next_output_net(),
                ce0net=luts.get_next_output_net(),
            ),
            file=bufgs)

    any_bufhce = False
    for tile_name, sites in gen_bufhce_sites():
        for site in sites:
            if not bufhce_in_todo(todos, site):
                continue

            any_bufhce = True
            print(
                """
    wire I_{site};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    BUFHCE buf_{site} (
        .I(I_{site})
    );
                    """.format(site=site, ),
                file=bufhs)

            if random.random() > .05:
                wire_name = clock_sources.get_random_source(site_to_cmt[site])

                if wire_name is None:
                    continue

                print(
                    """
    assign I_{site} = {wire_name};""".format(
                        site=site,
                        wire_name=wire_name,
                    ),
                    file=bufhs)

    if not any_bufhce:
        for tile_name, sites in gen_bufhce_sites():
            for site in sites:
                print(
                    """
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    BUFHCE #(
        .INIT_OUT({INIT_OUT}),
        .CE_TYPE({CE_TYPE}),
        .IS_CE_INVERTED({IS_CE_INVERTED})
    ) buf_{site} (
        .I({wire_name})
    );
              """.format(
                        INIT_OUT=random.randint(0, 1),
                        CE_TYPE=verilog.quote(
                            random.choice(('SYNC', 'ASYNC'))),
                        IS_CE_INVERTED=random.randint(0, 1),
                        site=site,
                        wire_name=gclks[0],
                    ))
                break
            break

    for l in luts.create_wires_and_luts():
        print(l)

    print(bufhs.getvalue())
    print(bufgs.getvalue())

    used_only = random.random() < .25

    for loc, tile_type, site in sorted(gen_sites("BUFGCTRL"),
                                       key=lambda x: BUFGCTRL_XY_FUN(x[2])):
        if random.randint(0, 1):
            wire_name = clock_sources.get_bufg_source(
                loc, tile_type, site, todos, 1, used_only)
            if wire_name is not None:
                print(
                    """
    assign I1_{site} = {wire_name};""".format(
                        site=site,
                        wire_name=wire_name,
                    ))

        if random.randint(0, 1):
            wire_name = clock_sources.get_bufg_source(
                loc, tile_type, site, todos, 0, used_only)
            if wire_name is not None:
                print(
                    """
    assign I0_{site} = {wire_name};""".format(
                        site=site,
                        wire_name=wire_name,
                    ))

    print("endmodule")


if __name__ == '__main__':
    main()
