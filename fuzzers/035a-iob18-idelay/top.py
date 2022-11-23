#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2022  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

import os, random
random.seed(int(os.getenv("SEED"), 16))

import re
import json

from prjxray import util
from prjxray.db import Database

# =============================================================================


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    tile_list = []
    for tile_name in sorted(grid.tiles()):
        if "IOB18" not in tile_name or "SING" in tile_name:
            continue
        tile_list.append(tile_name)

    get_xy = util.create_xy_fun('RIOB18_')
    tile_list.sort(key=get_xy)

    for iob_tile_name in tile_list:
        iob_gridinfo = grid.gridinfo_at_loc(
            grid.loc_of_tilename(iob_tile_name))

        # Find IOI tile adjacent to IOB
        for suffix in ["IOI", "IOI_TBYTESRC", "IOI_TBYTETERM"]:
            try:
                ioi_tile_name = iob_tile_name.replace("IOB18", suffix)
                ioi_gridinfo = grid.gridinfo_at_loc(
                    grid.loc_of_tilename(ioi_tile_name))
                break
            except KeyError:
                pass

        iob18s = [k for k, v in iob_gridinfo.sites.items() if v == "IOB18S"][0]
        iob18m = [k for k, v in iob_gridinfo.sites.items() if v == "IOB18M"][0]
        idelay_s = iob18s.replace("IOB", "IDELAY")
        idelay_m = iob18m.replace("IOB", "IDELAY")

        yield iob18m, idelay_m, iob18s, idelay_s


def run():

    # Get all [LR]IOI3 tiles
    tiles = list(gen_sites())

    # Header
    print("// Tile count: %d" % len(tiles))
    print("// Seed: '%s'" % os.getenv("SEED"))

    ninputs = 0
    di_idx = []
    for i, sites in enumerate(tiles):
        if random.randint(0, 1):
            di_idx.append(ninputs)
            ninputs += 1
        else:
            di_idx.append(None)

    print(
        '''
module top (
  (* CLOCK_BUFFER_TYPE = "NONE" *)
  input  wire clk,
  input  wire [{N}:0] di
);

wire clk_buf = clk;

wire [{N}:0] di_buf;
    '''.format(N=ninputs - 1))

    # LOCes IOBs
    data = []
    for i, (sites, ibuf_idx) in enumerate(zip(tiles, di_idx)):

        if random.randint(0, 1):
            iob_i = sites[0]
            iob_o = sites[2]
            idelay = sites[1]
            other_idelay = sites[3]
        else:
            iob_i = sites[2]
            iob_o = sites[0]
            idelay = sites[3]
            other_idelay = sites[1]

        use_ibuf = ibuf_idx is not None

        DELAY_SRC = random.choice(["IDATAIN", "DATAIN"])
        if not use_ibuf:
            DELAY_SRC = 'DATAIN'

        params = {
            "LOC":
            "\"" + idelay + "\"",
            "IDELAY_TYPE":
            "\"" + random.choice(
                ["FIXED", "VARIABLE", "VAR_LOAD", "VAR_LOAD_PIPE"]) + "\"",
            "IDELAY_VALUE":
            random.randint(0, 31),
            "DELAY_SRC":
            "\"" + DELAY_SRC + "\"",
            "HIGH_PERFORMANCE_MODE":
            "\"" + random.choice(["TRUE", "FALSE"]) + "\"",
            "CINVCTRL_SEL":
            "\"" + random.choice(["TRUE", "FALSE"]) + "\"",
            "PIPE_SEL":
            "\"" + random.choice(["TRUE", "FALSE"]) + "\"",
            "IS_C_INVERTED":
            random.randint(0, 1),
            "IS_DATAIN_INVERTED":
            random.randint(0, 1),
            "IS_IDATAIN_INVERTED":
            random.randint(0, 1),
        }

        if params["IDELAY_TYPE"] != "\"VAR_LOAD_PIPE\"":
            params["PIPE_SEL"] = "\"FALSE\""

        # The datasheet says that for these two modes the delay is set to 0
        if params["IDELAY_TYPE"] == "\"VAR_LOAD\"":
            params["IDELAY_VALUE"] = 0
        if params["IDELAY_TYPE"] == "\"VAR_LOAD_PIPE\"":
            params["IDELAY_VALUE"] = 0

        if params["IDELAY_TYPE"] == "\"FIXED\"":
            params["IS_C_INVERTED"] = 0

        param_str = ",".join(".%s(%s)" % (k, v) for k, v in params.items())

        if use_ibuf:
            print('')
            print('(* LOC="%s", KEEP, DONT_TOUCH *)' % iob_i)
            print(
                'IBUF ibuf_%03d (.I(di[%3d]), .O(di_buf[%3d]));' %
                (ibuf_idx, ibuf_idx, ibuf_idx))
            print(
                'mod #(%s) mod_%03d (.clk(clk_buf), .I(di_buf[%3d]));' %
                (param_str, i, ibuf_idx))
        else:
            print('mod #(%s) mod_%03d (.clk(clk_buf), .I());' % (param_str, i))

        params['IBUF_IN_USE'] = use_ibuf
        params["IDELAY_IN_USE"] = idelay
        params["IDELAY_NOT_IN_USE"] = other_idelay

        data.append(params)

    # Store params
    with open("params.json", "w") as fp:
        json.dump(data, fp, sort_keys=True, indent=1)

    print(
        '''
// IDELAYCTRL
(* KEEP, DONT_TOUCH *)
IDELAYCTRL idelayctrl();

endmodule

(* KEEP, DONT_TOUCH *)
module mod(
  input  wire clk,
  input  wire I
);

parameter LOC = "";
parameter IDELAY_TYPE = "FIXED";
parameter IDELAY_VALUE = 0;
parameter DELAY_SRC = "IDATAIN";
parameter HIGH_PERFORMANCE_MODE = "TRUE";
parameter SIGNAL_PATTERN = "DATA";
parameter CINVCTRL_SEL = "FALSE";
parameter PIPE_SEL = "FALSE";
parameter IS_C_INVERTED = 0;
parameter IS_DATAIN_INVERTED = 0;
parameter IS_IDATAIN_INVERTED = 0;

wire x;
wire lut;

(* KEEP, DONT_TOUCH *)
LUT2 l( .O(lut) );

// IDELAY
(* LOC=LOC, KEEP, DONT_TOUCH *)
IDELAYE2 #(
  .IDELAY_TYPE(IDELAY_TYPE),
  .IDELAY_VALUE(IDELAY_VALUE),
  .DELAY_SRC(DELAY_SRC),
  .HIGH_PERFORMANCE_MODE(HIGH_PERFORMANCE_MODE),
  .SIGNAL_PATTERN(SIGNAL_PATTERN),
  .CINVCTRL_SEL(CINVCTRL_SEL),
  .PIPE_SEL(PIPE_SEL),
  .IS_C_INVERTED(IS_C_INVERTED),
  .IS_DATAIN_INVERTED(IS_DATAIN_INVERTED),
  .IS_IDATAIN_INVERTED(IS_IDATAIN_INVERTED)
)
idelay
(
  .C(clk),
  .REGRST(),
  .LD(),
  .CE(),
  .INC(),
  .CINVCTRL(),
  .CNTVALUEIN(),
  .IDATAIN(I),
  .DATAIN(lut),
  .LDPIPEEN(),
  .DATAOUT(x),
  .CNTVALUEOUT()
);

endmodule
    ''')


run()
