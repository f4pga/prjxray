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

import json
import os
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import verilog
from prjxray.db import Database
from params import boolean_params, hex_params, int_params


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        if gridinfo.tile_type not in ["PCIE_BOT"]:
            continue

        for site_name, site_type in gridinfo.sites.items():

            return site_name, site_type


def main():
    print('''
module top();
''')

    lines = []

    site_name, site_type = gen_sites()

    params = dict()
    params['site'] = site_name

    verilog_attr = ""

    verilog_attr = "#("

    # Add boolean parameters
    for param, _ in boolean_params:
        value = random.randint(0, 1)
        value_string = "TRUE" if value else "FALSE"

        params[param] = value

        verilog_attr += """
    .{}({}),""".format(param, verilog.quote(value_string))

    # Add hexadecimal parameters
    for param, digits in hex_params:
        value = random.randint(0, 2**digits)

        params[param] = value

        verilog_attr += """
    .{}({}),""".format(
            param, "{digits}'h{value:08x}".format(value=value, digits=digits))

    # Add integer parameters
    for param, digits in int_params:
        value = random.randint(0, 2**digits)

        params[param] = value

        verilog_attr += """
    .{}({}),""".format(
            param, "{digits}'d{value:04d}".format(value=value, digits=digits))

    verilog_attr = verilog_attr.rstrip(",")
    verilog_attr += "\n)"

    print("PCIE_2_1 {} pcie ();".format(verilog_attr))
    print("endmodule")

    with open('params.json', 'w') as f:
        json.dump(params, f, indent=2)


if __name__ == '__main__':
    main()
