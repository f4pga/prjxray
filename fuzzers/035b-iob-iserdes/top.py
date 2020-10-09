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
import os, random
random.seed(int(os.getenv("SEED"), 16))

import json

from prjxray import util
from prjxray import verilog
from prjxray.db import Database

# =============================================================================


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    tile_list = []
    for tile_name in sorted(grid.tiles()):
        if "IOB33" not in tile_name or "SING" in tile_name:
            continue
        tile_list.append(tile_name)

    get_xy = util.create_xy_fun('[LR]IOB33_')
    tile_list.sort(key=get_xy)

    for iob_tile_name in tile_list:
        iob_gridinfo = grid.gridinfo_at_loc(
            grid.loc_of_tilename(iob_tile_name))

        iob33s = [k for k, v in iob_gridinfo.sites.items() if v == "IOB33S"][0]
        iob33m = [k for k, v in iob_gridinfo.sites.items() if v == "IOB33M"][0]

        top_sites = {
            "IOB": iob33m,
            "ILOGIC": iob33m.replace("IOB", "ILOGIC"),
            "IDELAY": iob33m.replace("IOB", "IDELAY"),
        }

        bot_sites = {
            "IOB": iob33s,
            "ILOGIC": iob33s.replace("IOB", "ILOGIC"),
            "IDELAY": iob33s.replace("IOB", "IDELAY"),
        }

        yield iob_tile_name, top_sites, bot_sites


def gen_iserdes(loc):

    # Site params
    params = {
        "SITE_LOC": verilog.quote(loc),
        "USE_IDELAY": random.randint(0, 1),
        "BEL_TYPE": verilog.quote("ISERDESE2"),
        "INIT_Q1": random.randint(0, 1),
        "INIT_Q2": random.randint(0, 1),
        "INIT_Q3": random.randint(0, 1),
        "INIT_Q4": random.randint(0, 1),
        "SRVAL_Q1": random.randint(0, 1),
        "SRVAL_Q2": random.randint(0, 1),
        "SRVAL_Q3": random.randint(0, 1),
        "SRVAL_Q4": random.randint(0, 1),
        "NUM_CE": random.randint(1, 2),

        # The following one shows negative correlation (0 - not inverted)
        "IS_D_INVERTED": random.randint(0, 1),

        # No bits were found for parameters below
        "IS_OCLKB_INVERTED": random.randint(0, 1),
        "IS_OCLK_INVERTED": random.randint(0, 1),
        "IS_CLKDIVP_INVERTED": random.randint(0, 1),
        "IS_CLKDIV_INVERTED": random.randint(0, 1),
        "IS_CLKB_INVERTED": random.randint(0, 1),
        "IS_CLK_INVERTED": random.randint(0, 1),
        "DYN_CLKDIV_INV_EN": verilog.quote(random.choice(["TRUE", "FALSE"])),
        "DYN_CLK_INV_EN": verilog.quote(random.choice(["TRUE", "FALSE"])),
        "IOBDELAY": verilog.quote(
            random.choice(["NONE", "IBUF", "IFD", "BOTH"])),
        "OFB_USED": verilog.quote(
            random.choice(["TRUE"] + ["FALSE"] * 9)),  # Force more FALSEs
    }

    iface_type = random.choice(
        ["NETWORKING", "OVERSAMPLE", "MEMORY", "MEMORY_DDR3", "MEMORY_QDR"])
    data_rate = random.choice(["SDR", "DDR"])
    serdes_mode = random.choice(["MASTER", "SLAVE"])

    params["INTERFACE_TYPE"] = verilog.quote(iface_type)
    params["DATA_RATE"] = verilog.quote(data_rate)
    params["SERDES_MODE"] = verilog.quote(serdes_mode)

    # Networking mode
    if iface_type == "NETWORKING":
        data_widths = {
            "SDR": [2, 3, 4, 5, 6, 7, 8],
            "DDR": [4, 6, 8, 10, 14],
        }
        params["DATA_WIDTH"] = random.choice(data_widths[data_rate])

    # Others
    else:
        params["DATA_WIDTH"] = 4

    if verilog.unquote(params["OFB_USED"]) == "TRUE":
        params["IOBDELAY"] = verilog.quote("NONE")

    return params


def gen_iddr(loc):

    # Site params
    params = {
        "SITE_LOC":
        verilog.quote(loc),
        "USE_IDELAY":
        random.randint(0, 1),
        "BEL_TYPE":
        verilog.quote(random.choice(["IDDR", "IDDR_NO_CLK"])),
        "INIT_Q1":
        random.randint(0, 1),
        "INIT_Q2":
        random.randint(0, 1),
        "SRTYPE":
        verilog.quote(random.choice(["ASYNC", "SYNC"])),
        "DDR_CLK_EDGE":
        verilog.quote(
            random.choice(
                ["OPPOSITE_EDGE", "SAME_EDGE", "SAME_EDGE_PIPELINED"])),
        "CE1USED":
        random.randint(0, 1),
        "SR_MODE":
        verilog.quote(random.choice(["NONE", "SET", "RST"])),
        "IS_C_INVERTED":
        random.randint(0, 1),
        "IS_D_INVERTED":
        random.randint(0, 1),
    }

    if params["USE_IDELAY"]:
        params["IDELMUX"] = random.randint(0, 1)
        params["IFFDELMUX"] = random.randint(0, 1)
    else:
        params["IDELMUX"] = 0
        params["IFFDELMUX"] = 0

    return params


def run():

    # Get all [LR]IOI3 tiles
    tiles = list(gen_sites())

    # Header
    print("// Tile count: %d" % len(tiles))
    print("// Seed: '%s'" % os.getenv("SEED"))
    print(
        '''
module top (
  (* CLOCK_BUFFER_TYPE = "NONE" *)
  input  wire clk1,
  (* CLOCK_BUFFER_TYPE = "NONE" *)
  input  wire clk2,
  input  wire ce,
  input  wire rst,
  input  wire [{N}:0] di,
  output wire [{N}:0] do
);

wire [{N}:0] di_buf;
wire [{N}:0] do_buf;

// IDELAYCTRL
(* KEEP, DONT_TOUCH *)
IDELAYCTRL idelayctrl();
    '''.format(**{"N": len(tiles) - 1}))

    # LOCes IOBs
    data = []
    for i, sites in enumerate(tiles):
        tile_name = sites[0]

        # Use site
        if random.randint(0, 19) > 0:  # Use more often

            # Top sites
            if random.randint(0, 1):
                this_sites = sites[1]
                other_sites = sites[2]
            # Bottom sites
            else:
                this_sites = sites[2]
                other_sites = sites[1]

            # Generate cell
            bel_types = ["IDDR", "ISERDESE2"]
            bel_type = bel_types[int(
                random.randint(0, 2) > 0)]  # ISERDES more often
            if bel_type == "ISERDESE2":
                params = gen_iserdes(this_sites["ILOGIC"])
            if bel_type == "IDDR":
                params = gen_iddr(this_sites["ILOGIC"])

            params["IDELAY_LOC"] = verilog.quote(this_sites["IDELAY"])
            params["IS_USED"] = 1

            # Instantiate the cell
            print('')
            print('// This : ' + " ".join(this_sites.values()))
            print('// Other: ' + " ".join(other_sites.values()))
            print('(* LOC="%s", KEEP, DONT_TOUCH *)' % this_sites["IOB"])
            print('IBUF ibuf_%03d (.I(di[%3d]), .O(di_buf[%3d]));' % (i, i, i))
            print('(* LOC="%s", KEEP, DONT_TOUCH *)' % other_sites["IOB"])
            print('OBUF obuf_%03d (.I(do_buf[%3d]), .O(do[%3d]));' % (i, i, i))

            clk1_conn = random.choice(["clk1", ""])

            param_str = ",".join(".%s(%s)" % (k, v) for k, v in params.items())
            print(
                'ilogic_single #(%s) ilogic_%03d (.clk1(%s), .clk2(clk2), .ce(ce), .rst(rst), .I(di_buf[%3d]), .O(do_buf[%3d]));'
                % (param_str, i, clk1_conn, i, i))

            params["CHAINED"] = 0
            params["TILE_NAME"] = tile_name

            # Params for the second site
            other_params = {
                "TILE_NAME": tile_name,
                "SITE_LOC": verilog.quote(other_sites["ILOGIC"]),
                "IDELAY_LOC": verilog.quote(other_sites["IDELAY"]),
                "IS_USED": 0,
            }

            # Append to data list
            data.append([params, other_params])

        # Don't use sites
        else:

            params_list = [
                {
                    "TILE_NAME": tile_name,
                    "SITE_LOC": verilog.quote(sites[1]["ILOGIC"]),
                    "IDELAY_LOC": verilog.quote(sites[1]["IDELAY"]),
                    "IS_USED": 0,
                },
                {
                    "TILE_NAME": tile_name,
                    "SITE_LOC": verilog.quote(sites[2]["ILOGIC"]),
                    "IDELAY_LOC": verilog.quote(sites[2]["IDELAY"]),
                    "IS_USED": 0,
                }
            ]

            data.append(params_list)

    # Store params
    with open("params.json", "w") as fp:
        json.dump(data, fp, sort_keys=True, indent=1)

    print(
        '''
endmodule

(* KEEP, DONT_TOUCH *)
module ilogic_single(
  input  wire clk1,
  input  wire clk2,
  input  wire ce,
  input  wire rst,
  input  wire I,
  output wire O,
  input  wire [1:0] shiftin,
  output wire [1:0] shiftout
);

parameter SITE_LOC = "";
parameter IS_USED = 1;
parameter BEL_TYPE = "ISERDESE2";
parameter IDELAY_LOC = "";
parameter USE_IDELAY = 0;
parameter IDELMUX = 0;
parameter IFFDELMUX = 0;
parameter INTERFACE_TYPE = "NETWORKING";
parameter DATA_RATE = "DDR";
parameter DATA_WIDTH = 4;
parameter SERDES_MODE = "MASTER";
parameter NUM_CE = 2;
parameter INIT_Q1 = 0;
parameter INIT_Q2 = 0;
parameter INIT_Q3 = 0;
parameter INIT_Q4 = 0;
parameter SRVAL_Q1 = 0;
parameter SRVAL_Q2 = 0;
parameter SRVAL_Q3 = 0;
parameter SRVAL_Q4 = 0;
parameter IS_D_INVERTED = 0;
parameter IS_OCLK_INVERTED = 0;
parameter IS_OCLKB_INVERTED = 0;
parameter IS_CLK_INVERTED = 0;
parameter IS_CLKB_INVERTED = 0;
parameter IS_CLKDIV_INVERTED = 0;
parameter IS_CLKDIVP_INVERTED = 0;
parameter DYN_CLKDIV_INV_EN = "FALSE";
parameter DYN_CLK_INV_EN = "FALSE";
parameter IOBDELAY = "NONE";
parameter OFB_USED = "FALSE";
parameter DDR_CLK_EDGE = "OPPOSITE_EDGE";
parameter SRTYPE = "ASYNC";
parameter CE1USED = 0;
parameter SR_MODE = "NONE";
parameter IS_C_INVERTED = 0;

wire [8:0] x;
wire ddly;

(* KEEP, DONT_TOUCH *)
generate if (IS_USED && USE_IDELAY) begin

  // IDELAY
  (* LOC=IDELAY_LOC, KEEP, DONT_TOUCH *)
  IDELAYE2 idelay
  (
    .C(clk),
    .REGRST(),
    .LD(),
    .CE(),
    .INC(),
    .CINVCTRL(),
    .CNTVALUEIN(),
    .IDATAIN(I),
    .DATAIN(),
    .LDPIPEEN(),
    .DATAOUT(ddly),
    .CNTVALUEOUT()
  );

end else begin

  assign ddly = 0;

end endgenerate

(* KEEP, DONT_TOUCH *)
generate if (IS_USED && BEL_TYPE == "ISERDESE2") begin

  // ISERDES
  (* LOC=SITE_LOC, KEEP, DONT_TOUCH *)
  ISERDESE2 #
  (
  .INTERFACE_TYPE(INTERFACE_TYPE),
  .DATA_RATE(DATA_RATE),
  .DATA_WIDTH(DATA_WIDTH),
  .SERDES_MODE(SERDES_MODE),
  .NUM_CE(NUM_CE),
  .IS_D_INVERTED(IS_D_INVERTED),
  .IS_OCLK_INVERTED(IS_OCLK_INVERTED),
  .IS_OCLKB_INVERTED(IS_OCLKB_INVERTED),
  .IS_CLK_INVERTED(IS_CLK_INVERTED),
  .IS_CLKB_INVERTED(IS_CLKB_INVERTED),
  .IS_CLKDIV_INVERTED(IS_CLKDIV_INVERTED),
  .IS_CLKDIVP_INVERTED(IS_CLKDIVP_INVERTED),
  .INIT_Q1(INIT_Q1),
  .INIT_Q2(INIT_Q2),
  .INIT_Q3(INIT_Q3),
  .INIT_Q4(INIT_Q4),
  .SRVAL_Q1(SRVAL_Q1),
  .SRVAL_Q2(SRVAL_Q2),
  .SRVAL_Q3(SRVAL_Q3),
  .SRVAL_Q4(SRVAL_Q4),
  .DYN_CLKDIV_INV_EN(DYN_CLKDIV_INV_EN),
  .DYN_CLK_INV_EN(DYN_CLK_INV_EN),
  .IOBDELAY(IOBDELAY),
  .OFB_USED(OFB_USED)
  )
  isedres
  (
  .D(I),
  .DDLY(),
  .OFB(),
  //.TFB(),
  .CE1(),
  .CE2(),
  .DYNCLKSEL(),
  .CLK(clk1),
  .CLKB(clk2),
  .OCLK(),
  .OCLKB(),
  .DYNCLKDIVSEL(),
  .CLKDIV(),
  .CLKDIVP(),
  .RST(),
  .BITSLIP(),
  .O(x[8]),
  .Q1(x[0]),
  .Q2(x[1]),
  .Q3(x[2]),
  .Q4(x[3]),
  .Q5(x[4]),
  .Q6(x[5]),
  .Q7(x[6]),
  .Q8(x[7]),
  .SHIFTIN1(shiftin[0]),
  .SHIFTIN2(shiftin[1]),
  .SHIFTOUT1(shiftout[0]),
  .SHIFTOUT2(shiftout[1])
  );

end else if (IS_USED && BEL_TYPE == "IDDR") begin

  // IDDR
  (* LOC=SITE_LOC, KEEP, DONT_TOUCH *)
  IDDR #
  (
  .IS_C_INVERTED(IS_C_INVERTED),
  .IS_D_INVERTED(IS_D_INVERTED),
  .DDR_CLK_EDGE(DDR_CLK_EDGE),
  .INIT_Q1(INIT_Q1),
  .INIT_Q2(INIT_Q2),
  .SRTYPE(SRTYPE)
  )
  iddr
  (
  .C(clk1),
  .CE( (CE1USED) ? ce : 1'hx ),
  .D( (IFFDELMUX) ? ddly : I  ),
  .S( (SR_MODE == "SET") ? rst : 1'd0 ),
  .R( (SR_MODE == "RST") ? rst : 1'd0 ),
  .Q1(x[0]),
  .Q2(x[1])
  );

  assign x[8] = (IDELMUX) ? ddly : I;
  assign x[7:2] = 0;

end else if (IS_USED && BEL_TYPE == "IDDR_NO_CLK") begin

  // IDDR
  (* LOC=SITE_LOC, KEEP, DONT_TOUCH *)
  IDDR #
  (
  .IS_C_INVERTED(IS_C_INVERTED),
  .IS_D_INVERTED(IS_D_INVERTED),
  .DDR_CLK_EDGE(DDR_CLK_EDGE),
  .INIT_Q1(INIT_Q1),
  .INIT_Q2(INIT_Q2),
  .SRTYPE(SRTYPE)
  )
  iddr
  (
  .C(),
  .CE( (CE1USED) ? ce : 1'hx ),
  .D( (IFFDELMUX) ? ddly : I  ),
  .S( (SR_MODE == "SET") ? rst : 1'd0 ),
  .R( (SR_MODE == "RST") ? rst : 1'd0 ),
  .Q1(x[0]),
  .Q2(x[1])
  );

  assign x[8] = (IDELMUX) ? ddly : I;
  assign x[7:2] = 0;

end else begin

  assign x[0] = I;
  assign x[1] = I;
  assign x[2] = I;
  assign x[3] = I;
  assign x[4] = I;
  assign x[5] = I;
  assign x[6] = I;
  assign x[7] = I;
  assign x[8] = I;

end endgenerate

// Output
assign O = |x;

endmodule

    ''')


run()
