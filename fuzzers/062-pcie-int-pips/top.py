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
from prjxray.lut_maker import LutMaker
from prjxray.db import Database

from ports import ports


def print_site(ports, luts, site, site_type):
    verilog_ports = ""
    verilog_wires = ""

    for port, width in ports:
        verilog_ports += """
    .{port}({port}_{site}),""".format(
            port=port, site=site)
        verilog_wires += "wire [{}:0] {}_{};\n".format(width - 1, port, site)

        for idx in range(0, width):
            verilog_wires += "assign {}_{}[{}] = {};\n".format(
                port, site, idx, luts.get_next_output_net())

        verilog_wires += "\n"

    verilog_ports = verilog_ports.rstrip(",")

    print(
        """
{wires}

(* KEEP, DONT_TOUCH, LOC = "{site}" *)
{site_type} {site}_instance (
{ports}
);""".format(
            wires=verilog_wires,
            ports=verilog_ports,
            site=site,
            site_type=site_type))


def main():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    luts = LutMaker()

    def gen_sites(desired_site_type):
        for tile_name in sorted(grid.tiles()):
            loc = grid.loc_of_tilename(tile_name)
            gridinfo = grid.gridinfo_at_loc(loc)
            for site, site_type in gridinfo.sites.items():
                if site_type == desired_site_type:
                    yield tile_name, site

    print('''
module top();

    (* KEEP, DONT_TOUCH *)
    LUT6 dummy();
''')

    for site_type in ["PCIE_2_1"]:
        for _, site in gen_sites(site_type):
            print_site(ports[site_type], luts, site, site_type)

    for l in luts.create_wires_and_luts():
        print(l)

    print('endmodule')


if __name__ == "__main__":
    main()
