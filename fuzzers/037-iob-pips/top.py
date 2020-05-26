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

NOT_INCLUDED_TILES = ['LIOI3_SING', 'RIOI3_SING']

SITE_TYPES = ['OLOGICE3', 'ILOGICE3']


def read_site_to_cmt():
    """ Yields clock sources and which CMT they route within. """
    with open(os.path.join(os.getenv('FUZDIR'), 'build',
                           'cmt_regions.csv')) as f:
        for l in f:
            site, cmt = l.strip().split(',')
            yield (site, cmt)


def gen_sites():
    ''' Return dict of ISERDES/OSERDES locations. '''
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    xy_fun = util.create_xy_fun('\S+')

    tiles = grid.tiles()

    for tile_name in sorted(tiles):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        tile_type = gridinfo.tile_type

        tile = {'tile': tile_name, 'tile_type': tile_type, 'ioi_sites': {}}

        for site_name, site_type in gridinfo.sites.items():
            if site_type in SITE_TYPES:
                xy = xy_fun(site_name)
                if xy not in tile['ioi_sites']:
                    tile['ioi_sites'][xy] = {}

                tile['ioi_sites'][xy][site_type] = site_name

        yield tile


class ClockSources(object):
    def __init__(self):
        self.site_to_cmt = dict(read_site_to_cmt())

        self.leaf_gclks = {}
        self.ioclks = {}
        self.rclks = {}
        self.selected_leaf_gclks = {}
        self.lut_maker = lut_maker.LutMaker()

        for cmt in set(self.site_to_cmt.values()):
            self.leaf_gclks[cmt] = []
            self.ioclks[cmt] = []
            self.rclks[cmt] = []

    def init_clocks(self):
        """ Initialize all IOI clock sources. """
        for site, cmt in self.site_to_cmt.items():
            clk = 'clk_' + site
            if 'BUFHCE' in site:
                print(
                    """
            wire {clk};
            (* KEEP, DONT_TOUCH, LOC = "{site}" *)
            BUFH bufh_{site}(
                .O({clk})
                );
                """.format(
                        clk=clk,
                        site=site,
                    ))

                self.leaf_gclks[cmt].append(clk)

            if 'BUFIO' in site:
                print(
                    """
            wire {clk};
            (* KEEP, DONT_TOUCH, LOC = "{site}" *)
            BUFIO bufio_{site}(
                .O({clk})
                );
                """.format(
                        clk=clk,
                        site=site,
                    ))

                self.ioclks[cmt].append(clk)

            if 'BUFR' in site:
                print(
                    """
            wire {clk};
            (* KEEP, DONT_TOUCH, LOC = "{site}" *)
            BUFR bufr_{site}(
                .O({clk})
                );
                """.format(
                        clk=clk,
                        site=site,
                    ))

                self.rclks[cmt].append(clk)

        # Choose 6 leaf_gclks to be used in each CMT.
        for cmt in self.leaf_gclks:
            self.selected_leaf_gclks[cmt] = random.sample(
                self.leaf_gclks[cmt], 6)

    def get_clock(
            self,
            site,
            allow_ioclks,
            allow_rclks,
            allow_fabric=True,
            allow_empty=True):
        cmt = self.site_to_cmt[site]
        choices = []
        if allow_fabric:
            choices.append('lut')

        if allow_empty:
            choices.append('')

        choices.extend(self.selected_leaf_gclks[cmt])
        if allow_ioclks:
            choices.extend(self.ioclks[cmt])

        if allow_rclks:
            choices.extend(self.rclks[cmt])

        clock = random.choice(choices)
        is_lut = False
        if clock == "lut":
            clock = self.lut_maker.get_next_output_net()
            is_lut = True
        return clock, is_lut


def add_port(ports, port, signal):
    ports.append('.{}({})'.format(port, signal))


def run():
    print("module top();")

    clocks = ClockSources()
    clocks.init_clocks()
    """

    ISERDESE2 clock sources:

    CLK/CLKB:
     - Allows LEAF_GCLK, IOCLKS, RCLKS and fabric
     - Dedicated pips

    CLKDIV:
     - No dedicated pips, uses fabric clock in.

    CLKDIVP:
     - Has pips, MIG only, PHASER or fabric.

    OCLK/OCLKB:
     - Allows LEAF_GCLK, IOCLKS, RCLKS and fabric
     - Must match OSERDESE2:CLK/CLKB

     OSERDESE2 clock sources:

     CLKDIV/CLKDIVB:
      - Allows LEAF_GCLK and RCLKS and fabric
      - Dedicated pips

     CLKDIVF/CLKDIVFB:
      - Allows LEAF_GCLK and RCLKS and fabric
      - No explicit port, follows CLKDIV/CLKDIVB?
      """

    output = []
    route_file = open("routes.txt", "w")

    for tile in gen_sites():
        if tile['tile_type'] in NOT_INCLUDED_TILES:
            continue

        for xy in tile['ioi_sites']:
            ilogic_site_type = random.choice([None, 'ISERDESE2', 'IDDR'])
            use_oserdes = random.randint(0, 1)

            ilogic_site = tile['ioi_sites'][xy]['ILOGICE3']
            ologic_site = tile['ioi_sites'][xy]['OLOGICE3']

            if use_oserdes:
                oclk, _ = clocks.get_clock(
                    ologic_site, allow_ioclks=True, allow_rclks=True)

                oclkb = oclk
            else:
                oclk, is_lut = clocks.get_clock(
                    ilogic_site, allow_ioclks=True, allow_rclks=True)

                if random.randint(0, 1):
                    oclkb = oclk
                else:
                    if random.randint(0, 1):
                        oclkb, _ = clocks.get_clock(
                            ilogic_site,
                            allow_ioclks=True,
                            allow_rclks=True,
                            allow_fabric=not is_lut)
                    else:
                        # Explicitly provide IMUX stimulus to resolve IMUX pips
                        oclk = random.randint(0, 1)
                        oclkb = random.randint(0, 1)

            DATA_RATE = random.choice(['DDR', 'SDR'])
            clk, clk_is_lut = clocks.get_clock(
                ilogic_site,
                allow_ioclks=True,
                allow_rclks=True,
                allow_empty=DATA_RATE == 'SDR')

            clkb = clk
            while clkb == clk:
                clkb, clkb_is_lut = clocks.get_clock(
                    ilogic_site,
                    allow_ioclks=True,
                    allow_rclks=True,
                    allow_empty=False)

            imux_available = {
                0: set(("IOI_IMUX20_0", "IOI_IMUX22_0")),
                1: set(("IOI_IMUX20_1", "IOI_IMUX22_1")),
            }

            # Force CLK route through IMUX when connected to a LUT
            if clk_is_lut:
                y = (xy[1] + 1) % 2

                route = random.choice(list(imux_available[y]))
                imux_available[y].remove(route)

                route = "{}/{}".format(tile["tile"], route)
                route_file.write("{} {}\n".format(clk, route))

            # Force CLKB route through IMUX when connected to a LUT
            if clkb_is_lut:
                y = (xy[1] + 1) % 2

                route = random.choice(list(imux_available[y]))
                imux_available[y].remove(route)

                route = "{}/{}".format(tile["tile"], route)
                route_file.write("{} {}\n".format(clkb, route))

            if ilogic_site_type is None:
                pass

            elif ilogic_site_type == 'ISERDESE2':
                INTERFACE_TYPE = random.choice(
                    [
                        'MEMORY',
                        'MEMORY_DDR3',
                        'MEMORY_QDR',
                        'NETWORKING',
                        'OVERSAMPLE',
                    ])
                ports = []

                add_port(ports, 'CLK', clk)
                add_port(ports, 'CLKB', clkb)
                add_port(ports, 'OCLK', oclk)
                add_port(ports, 'OCLKB', oclkb)

                output.append(
                    """
            (* KEEP, DONT_TOUCH, LOC="{site}" *)
            ISERDESE2 #(
                .DATA_RATE({DATA_RATE}),
                .INTERFACE_TYPE({INTERFACE_TYPE}),
                .IS_CLK_INVERTED({IS_CLK_INVERTED}),
                .IS_CLKB_INVERTED({IS_CLKB_INVERTED}),
                .IS_OCLK_INVERTED({IS_OCLK_INVERTED}),
                .IS_OCLKB_INVERTED({IS_OCLKB_INVERTED}),
                .INIT_Q1({INIT_Q1}),
                .INIT_Q2({INIT_Q2}),
                .INIT_Q3({INIT_Q3}),
                .INIT_Q4({INIT_Q4}),
                .SRVAL_Q1({SRVAL_Q1}),
                .SRVAL_Q2({SRVAL_Q2}),
                .SRVAL_Q3({SRVAL_Q3}),
                .SRVAL_Q4({SRVAL_Q4})
            ) iserdes_{site}(
                {ports});""".format(
                        site=ilogic_site,
                        ports=',\n'.join(ports),
                        DATA_RATE=verilog.quote(DATA_RATE),
                        INTERFACE_TYPE=verilog.quote(INTERFACE_TYPE),
                        IS_CLK_INVERTED=random.randint(0, 1),
                        IS_CLKB_INVERTED=random.randint(0, 1),
                        IS_OCLK_INVERTED=random.randint(0, 1),
                        IS_OCLKB_INVERTED=random.randint(0, 1),
                        INIT_Q1=random.randint(0, 1),
                        INIT_Q2=random.randint(0, 1),
                        INIT_Q3=random.randint(0, 1),
                        INIT_Q4=random.randint(0, 1),
                        SRVAL_Q1=random.randint(0, 1),
                        SRVAL_Q2=random.randint(0, 1),
                        SRVAL_Q3=random.randint(0, 1),
                        SRVAL_Q4=random.randint(0, 1),
                    ))
            elif ilogic_site_type == 'IDDR':
                ports = []
                add_port(ports, 'C', clk)
                add_port(ports, 'CB', clkb)

                output.append(
                    """
            (* KEEP, DONT_TOUCH, LOC="{site}" *)
            IDDR_2CLK #(
                .INIT_Q1({INIT_Q1}),
                .INIT_Q2({INIT_Q2}),
                .SRTYPE({SRTYPE})
            ) iserdes_{site}(
                {ports});""".format(
                        site=ilogic_site,
                        ports=',\n'.join(ports),
                        INIT_Q1=random.randint(0, 1),
                        INIT_Q2=random.randint(0, 1),
                        SRTYPE=verilog.quote(random.choice(['ASYNC', 'SYNC'])),
                    ))
            else:
                assert False, ilogic_site_type

            if use_oserdes:
                ports = []

                add_port(
                    ports, 'CLKDIV',
                    clocks.get_clock(
                        ologic_site,
                        allow_ioclks=False,
                        allow_rclks=True,
                    )[0])

                add_port(ports, 'CLK', oclk)

                output.append(
                    """
            (* KEEP, DONT_TOUCH, LOC = "{site}" *)
            OSERDESE2 #(
                .IS_CLK_INVERTED({IS_CLK_INVERTED}),
                .DATA_RATE_OQ("SDR"),
                .DATA_RATE_TQ("SDR")
            ) oserdes_{site} (
                {ports});""".format(
                        IS_CLK_INVERTED=random.randint(0, 1),
                        site=ologic_site,
                        ports=',\n'.join(ports),
                    ))

    for s in clocks.lut_maker.create_wires_and_luts():
        print(s)

    for s in output:
        print(s)

    print("endmodule")


if __name__ == '__main__':
    run()
