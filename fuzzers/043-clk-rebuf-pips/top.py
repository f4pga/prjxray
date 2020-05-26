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
import itertools
import re
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray.db import Database

XY_RE = re.compile('^BUFHCE_X([0-9]+)Y([0-9]+)$')
BUFGCTRL_XY_RE = re.compile('^BUFGCTRL_X([0-9]+)Y([0-9]+)$')
"""
BUFHCE's can be driven from:

MMCME2_ADV
BUFHCE
PLLE2_ADV
BUFGCTRL
"""


def get_xy(s):
    m = BUFGCTRL_XY_RE.match(s)
    x = int(m.group(1))
    y = int(m.group(2))
    return x, y


def gen_sites(desired_site_type):
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        for site, site_type in gridinfo.sites.items():
            if site_type == desired_site_type:
                yield site


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
            yield tile_name, set(sites)


def main():
    print('''
module top();
    ''')

    gclks = []
    for site in sorted(gen_sites("BUFGCTRL"), key=get_xy):
        wire_name = 'clk_{}'.format(site)
        gclks.append(wire_name)

        print(
            """
    wire {wire_name};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    BUFG bufg_{site} (
        .O({wire_name})
        );
        """.format(
                site=site,
                wire_name=wire_name,
            ))

    bufhce_sites = list(gen_bufhce_sites())

    opts = []
    for count in range(len(bufhce_sites)):
        for opt in itertools.combinations(bufhce_sites, count + 1):
            opts.append(opt)

    for gclk in gclks:
        for tile_name, sites in random.choice(opts):
            for site in sorted(sites):
                print(
                    """
        (* KEEP, DONT_TOUCH, LOC = "{site}" *)
        BUFHCE buf_{site} (
            .I({wire_name})
                );""".format(
                        site=site,
                        wire_name=gclk,
                    ))
                sites.remove(site)
                break

    print("endmodule")


if __name__ == '__main__':
    main()
