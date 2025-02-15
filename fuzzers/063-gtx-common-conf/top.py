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


def gen_sites(tile, site, filter_cmt=None):
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        if tile not in gridinfo.tile_type:
            continue
        else:
            tile_type = gridinfo.tile_type

        for site_name, site_type in gridinfo.sites.items():
            if site_type != site:
                continue

            cmt = gridinfo.clock_region

            if filter_cmt is not None and cmt != filter_cmt:
                continue

            yield tile_name, tile_type, site_name, cmt


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

    params_dict = {"tile_type": None}
    params_list = list()

    clkswing_cfg_tiles = dict()
    ibufds_out_wires = dict()
    for tile_name, _, site_name, _ in gen_sites("GTX_COMMON", "IBUFDS_GTE2"):
        # Both the IBUFDS_GTE2 in the same tile need to have
        # the same CLKSWING_CFG parameter
        if tile_name not in clkswing_cfg_tiles:
            clkswing_cfg = random.randint(0, 3)
            clkswing_cfg_tiles[tile_name] = clkswing_cfg
        else:
            clkswing_cfg = clkswing_cfg_tiles[tile_name]

        in_use = bool(random.randint(0, 9))
        params = {
            "site":
            site_name,
            "tile":
            tile_name,
            "IN_USE":
            in_use,
            "CLKRCV_TRST":
            verilog.quote("TRUE" if random.randint(0, 1) else "FALSE"),
            "CLKCM_CFG":
            verilog.quote("TRUE" if random.randint(0, 1) else "FALSE"),
            "CLKSWING_CFG":
            clkswing_cfg,
        }

        if in_use:
            ibufds_out_wire = "{}_O".format(site_name)

            if tile_name not in ibufds_out_wires:
                ibufds_out_wires[tile_name] = list()

            ibufds_out_wires[tile_name].append(
                (ibufds_out_wire, int(site_name[-1]) % 2))

            print("wire {};".format(ibufds_out_wire))
            print("(* KEEP, DONT_TOUCH, LOC=\"{}\" *)".format(site_name))
            print(
                """
IBUFDS_GTE2 #(
    .CLKRCV_TRST({CLKRCV_TRST}),
    .CLKCM_CFG({CLKCM_CFG}),
    .CLKSWING_CFG({CLKSWING_CFG})
) {site} (
    .O({out})
);""".format(**params, out=ibufds_out_wire))

        params_list.append(params)

    DRP_PORTS = [
        ("DRPCLK", "clk"), ("DRPEN", "in"), ("DRPWE", "in"), ("DRPRDY", "out")
    ]

    for tile_name, tile_type, site_name, cmt in gen_sites("GTX_COMMON",
                                                          "GTXE2_COMMON"):

        params_dict["tile_type"] = tile_type

        params = dict()
        params['site'] = site_name
        params['tile'] = tile_name

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
                else:
                    assert param_type == BIN
                    value = random.randint(0, param_values[0])
                    value_str = "{digits}'b{value:0{digits}b}".format(
                        value=value, digits=param_digits)

                params[param] = value

                verilog_attr += """
            .{}({}),""".format(param, value_str)

            verilog_ports = ""

            for param in ["QPLLLOCKDETCLK", "DRPCLK"]:
                is_inverted = random.randint(0, 1)

                params[param] = is_inverted

                verilog_attr += """
            .IS_{}_INVERTED({}),""".format(param, is_inverted)
                verilog_ports += """
            .{}({}),""".format(param, luts.get_next_output_net())

            verilog_attr = verilog_attr.rstrip(",")
            verilog_attr += "\n)"

            for param in ["GTREFCLK0_USED", "GTREFCLK1_USED",
                          "BOTH_GTREFCLK_USED"]:
                params[param] = 0

            if tile_name in ibufds_out_wires:
                gtrefclk_ports_used = 0

                for wire, location in ibufds_out_wires[tile_name]:
                    if random.random() < 0.5:
                        continue

                    verilog_ports += """
            .GTREFCLK{}({}),""".format(location, wire)

                    gtrefclk_ports_used += 1
                    params["GTREFCLK{}_USED".format(location)] = 1

                if gtrefclk_ports_used == 2:
                    params["BOTH_GTREFCLK_USED"] = 1

            enable_drp = random.randint(0, 1)
            params["ENABLE_DRP"] = enable_drp

            for _, _, channel_site_name, _ in gen_sites("GTX_CHANNEL",
                                                        "GTXE2_CHANNEL", cmt):

                if not enable_drp:
                    break

                verilog_ports_channel = ""
                for port, direction in DRP_PORTS:
                    if direction == "in":
                        verilog_ports_channel += """
    .{}({}),""".format(port, luts.get_next_output_net())

                    elif direction == "clk":
                        # DRPCLK needs to come from a clock source
                        print(
                            """
wire clk_bufg_{site};

(* KEEP, DONT_TOUCH *)
BUFG bufg_{site} (.O(clk_bufg_{site}));""".format(site=channel_site_name))

                        verilog_ports_channel += """
    .{}(clk_bufg_{}),""".format(port, channel_site_name)

                    elif direction == "out":
                        verilog_ports_channel += """
    .{}({}),""".format(port, luts.get_next_input_net())

                print(
                    """
(* KEEP, DONT_TOUCH, LOC=\"{site}\" *)
GTXE2_CHANNEL {site} (
    {ports}
);""".format(ports=verilog_ports_channel.rstrip(","), site=channel_site_name))

            print(
                """
(* KEEP, DONT_TOUCH, LOC=\"{site}\" *)
GTXE2_COMMON {attrs} {site} (
    {ports}
);""".format(
                    attrs=verilog_attr,
                    ports=verilog_ports.rstrip(","),
                    site=site_name))

        params_list.append(params)

    for l in luts.create_wires_and_luts():
        print(l)

    print("endmodule")

    params_dict["params"] = params_list
    with open('params.json', 'w') as f:
        json.dump(params_dict, f, indent=2)


if __name__ == '__main__':
    main()
