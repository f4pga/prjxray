#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2023  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

import os, random
random.seed(int(os.getenv("SEED"), 16))

import sys
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
        odelay_s = iob18s.replace("IOB", "ODELAY")
        odelay_m = iob18m.replace("IOB", "ODELAY")

        yield iob18m, odelay_m, iob18s, odelay_s


def run():

    # Get all [LR]IOI3 tiles
    tiles = list(gen_sites())

    # Header
    print("// Tile count: %d" % len(tiles))
    print("// Seed: '%s'" % os.getenv("SEED"))

    ninputs = 0
    do_idx = []
    for i, sites in enumerate(tiles):
        if random.randint(0, 1):
            do_idx.append(ninputs)
            ninputs += 1
        else:
            do_idx.append(None)

    print(
        '''
module top (
  (* CLOCK_BUFFER_TYPE = "NONE" *)
  input  wire clk,
  output wire [{N}:0] do
);

wire clk_buf = clk;

wire [{N}:0] do_buf;
    '''.format(N=ninputs - 1))

    # LOCes IOBs
    data = []
    for i, (sites, obuf_idx) in enumerate(zip(tiles, do_idx)):

        if random.randint(0, 1):
            iob_inuse     = sites[0]
            iob_other     = sites[2]
            odelay_inuse  = sites[1]
            odelay_other  = sites[3]
        else:
            iob_inuse     = sites[2]
            iob_other     = sites[0]
            odelay_inuse  = sites[3]
            odelay_other  = sites[1]

        use_obuf = obuf_idx is not None

        if not use_obuf:
            continue

        params = {
            "LOC":
            "\"" + odelay_inuse + "\"",
            "ODELAY_TYPE":
            "\"" + random.choice(
                ["FIXED", "VARIABLE", "VAR_LOAD"]) + "\"",
            "ODELAY_VALUE":
            random.randint(0, 31),
            "HIGH_PERFORMANCE_MODE":
            "\"" + random.choice(["TRUE", "FALSE"]) + "\"",
            "CINVCTRL_SEL":
            "\"" + random.choice(["TRUE", "FALSE"]) + "\"",
            "PIPE_SEL":
            "\"" + random.choice(["TRUE", "FALSE"]) + "\"",
            "IS_C_INVERTED":
            random.randint(0, 1),
            "IS_ODATAIN_INVERTED":
            random.randint(0, 1),
        }

        if params["ODELAY_TYPE"] != "\"VAR_LOAD_PIPE\"":
            params["PIPE_SEL"] = "\"FALSE\""

        # The datasheet says that for these two modes the delay is set to 0
        if params["ODELAY_TYPE"] == "\"VAR_LOAD\"":
            params["ODELAY_VALUE"] = 0
        if params["ODELAY_TYPE"] == "\"VAR_LOAD_PIPE\"":
            params["ODELAY_VALUE"] = 0

        if params["ODELAY_TYPE"] == "\"FIXED\"":
            params["IS_C_INVERTED"] = 0

        param_str = ",".join(".%s(%s)" % (k, v) for k, v in params.items())

        if random.randint(0, 5) == 0:
            print('')
            print('(* LOC="%s", KEEP, DONT_TOUCH *)' % iob_inuse)
            print(
                'OBUF obuf_%03d (.I(%d), .O(do[%3d]));' %
                (obuf_idx, random.randint(0, 1), obuf_idx))
            params['ODELAY_BYPASS'] = True
            params["ODELAY_NOT_IN_USE"] = odelay_inuse + " " + odelay_other
        else:
            print('')
            print('(* LOC="%s", KEEP, DONT_TOUCH *)' % iob_inuse)
            print(
                'OBUF obuf_%03d (.I(do_buf[%3d]), .O(do[%3d]));' %
                (obuf_idx, obuf_idx, obuf_idx))
            print(
                'mod #(%s) mod_%03d (.clk(clk_buf), .O(do_buf[%3d]));' %
                (param_str, i, obuf_idx))
            params['ODELAY_BYPASS'] = False
            params["ODELAY_IN_USE"] = odelay_inuse
            params["ODELAY_NOT_IN_USE"] = odelay_other

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
  output  wire O
);

parameter LOC = "";
parameter ODELAY_TYPE = "FIXED";
parameter ODELAY_VALUE = 0;
parameter DELAY_SRC = "ODATAIN";
parameter HIGH_PERFORMANCE_MODE = "TRUE";
parameter SIGNAL_PATTERN = "DATA";
parameter CINVCTRL_SEL = "FALSE";
parameter PIPE_SEL = "FALSE";
parameter IS_C_INVERTED = 0;
parameter IS_ODATAIN_INVERTED = 0;

wire x;
wire lut;

(* KEEP, DONT_TOUCH *)
LUT2 l( .O(lut) );

// ODELAY
(* LOC=LOC, KEEP, DONT_TOUCH *)
ODELAYE2 #(
  .ODELAY_TYPE(ODELAY_TYPE),
  .ODELAY_VALUE(ODELAY_VALUE),
  .DELAY_SRC(DELAY_SRC),
  .HIGH_PERFORMANCE_MODE(HIGH_PERFORMANCE_MODE),
  .SIGNAL_PATTERN(SIGNAL_PATTERN),
  .CINVCTRL_SEL(CINVCTRL_SEL),
  .PIPE_SEL(PIPE_SEL),
  .IS_C_INVERTED(IS_C_INVERTED),
  .IS_ODATAIN_INVERTED(IS_ODATAIN_INVERTED)
)
odelay
(
  .C(clk),
  .REGRST(),
  .LD(),
  .CE(),
  .INC(),
  .CINVCTRL(),
  .CNTVALUEIN(),
  .ODATAIN(lut),
  .LDPIPEEN(),
  .DATAOUT(O),
  .CNTVALUEOUT()
);

endmodule
    ''')


run()
