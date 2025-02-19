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
from collections import namedtuple

random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import verilog
from prjxray.lut_maker import LutMaker
from prjxray.db import Database

INT = "INT"
BIN = "BIN"
BOOL = "BOOL"
STR = "STR"


def gen_sites(site):
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    already_used = list()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        if gridinfo.tile_type not in [
                "GTX_CHANNEL_0",
                "GTX_CHANNEL_1",
                "GTX_CHANNEL_2",
                "GTX_CHANNEL_3",
                "GTX_CHANNEL_0_MID_LEFT",
                "GTX_CHANNEL_1_MID_LEFT",
                "GTX_CHANNEL_2_MID_LEFT",
                "GTX_CHANNEL_3_MID_LEFT",
                "GTX_CHANNEL_0_MID_RIGHT",
                "GTX_CHANNEL_1_MID_RIGHT",
                "GTX_CHANNEL_2_MID_RIGHT",
                "GTX_CHANNEL_3_MID_RIGHT",
        ] or gridinfo.tile_type in already_used:
            continue
        else:
            tile_type = gridinfo.tile_type
            already_used.append(tile_type)

        for site_name, site_type in gridinfo.sites.items():
            if site_type != site:
                continue

            if "RIGHT" in tile_type and "X0" in site_name:
                continue

            if "LEFT" in tile_type and "X1" in site_name:
                continue

            yield tile_name, tile_type, site_name, site_type


def main():
    print(
        '''
module top(
    input wire in,
    output wire out
);

assign out = in;
''')

    luts = LutMaker()

    primitives_list = list()

    for tile_name, tile_type, site_name, site_type in gen_sites(
            "GTXE2_CHANNEL"):

        params_list = list()
        params_dict = dict()

        params_dict["tile_type"] = tile_type
        params = dict()
        params['site'] = site_name

        verilog_attr = ""

        verilog_attr = "#("

        fuz_dir = os.getenv("FUZDIR", None)
        assert fuz_dir
        with open(os.path.join(fuz_dir, "attrs.json"), "r") as attrs_file:
            attrs = json.load(attrs_file)

        in_use = bool(random.randint(0, 9))
        params["IN_USE"] = in_use

        if in_use:
            for param, param_info in attrs.items():
                param_type = param_info["type"]
                param_values = param_info["values"]
                param_digits = param_info["digits"]

                if param_type == INT:
                    value = random.choice(param_values)
                    value_str = value
                elif param_type == BIN:
                    value = random.randint(0, param_values[0])
                    value_str = "{digits}'b{value:0{digits}b}".format(
                        value=value, digits=param_digits)
                elif param_type in [BOOL, STR]:
                    value = random.choice(param_values)
                    value_str = verilog.quote(value)

                params[param] = value

                verilog_attr += """
            .{}({}),""".format(param, value_str)

            verilog_ports = ""
            for param in ["TXUSRCLK", "TXUSRCLK2", "TXPHDLYTSTCLK",
                          "RXUSRCLK", "RXUSRCLK2", "DRPCLK"]:
                is_inverted = random.randint(0, 1)

                params[param] = is_inverted

                verilog_attr += """
            .IS_{}_INVERTED({}),""".format(param, is_inverted)
                verilog_ports += """
            .{}({}),""".format(param, luts.get_next_output_net())

            verilog_attr = verilog_attr.rstrip(",")
            verilog_attr += "\n)"

            print("(* KEEP, DONT_TOUCH, LOC=\"{}\" *)".format(site_name))
            print(
                """GTXE2_CHANNEL {attrs} {site} (
    {ports}
);
            """.format(
                    attrs=verilog_attr,
                    site=tile_type.lower(),
                    ports=verilog_ports.rstrip(",")))

        params_list.append(params)
        params_dict["params"] = params_list
        primitives_list.append(params_dict)

    for l in luts.create_wires_and_luts():
        print(l)

    print("endmodule")

    with open('params.json', 'w') as f:
        json.dump(primitives_list, f, indent=2)


if __name__ == '__main__':
    main()
