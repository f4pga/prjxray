#!/usr/bin/env python3

import os, random
random.seed(int(os.getenv("SEED"), 16))

import re
import json

from prjxray import util
from prjxray import verilog
from prjxray.db import Database

# =============================================================================


def gen_sites():
    db = Database(util.get_db_root())
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

        # Find IOI tile adjacent to IOB
        for suffix in ["IOI3", "IOI3_TBYTESRC", "IOI3_TBYTETERM"]:
            try:
                ioi_tile_name = iob_tile_name.replace("IOB33", suffix)
                ioi_gridinfo = grid.gridinfo_at_loc(
                    grid.loc_of_tilename(ioi_tile_name))
                break
            except KeyError:
                pass

        iob33s = [k for k, v in iob_gridinfo.sites.items() if v == "IOB33S"][0]
        iob33m = [k for k, v in iob_gridinfo.sites.items() if v == "IOB33M"][0]
        ilogic_s = iob33s.replace("IOB", "ILOGIC")
        ilogic_m = iob33m.replace("IOB", "ILOGIC")

        yield iob_tile_name, iob33m, ilogic_m, iob33s, ilogic_s


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
  input  wire [{N}:0] di,
  output wire [{N}:0] do
);

wire [{N}:0] di_buf;
wire [{N}:0] do_buf;
    '''.format(**{"N": len(tiles) - 1}))

    # LOCes IOBs
    data = []
    for i, sites in enumerate(tiles):
        tile_name = sites[0]

        # Bottom site
        if random.randint(0, 1):
            iob_i = sites[1]
            iob_o = sites[3]
            ilogic = sites[2]
        # Top site
        else:
            iob_i = sites[3]
            iob_o = sites[1]
            ilogic = sites[4]

        # Site params
        params = {
            "_LOC":
            verilog.quote(ilogic),
            "IS_USED":
            int(random.randint(0, 10) > 0),  # Make it used more often
            "INIT_Q1":
            random.randint(0, 1),
            "INIT_Q2":
            random.randint(0, 1),
            "INIT_Q3":
            random.randint(0, 1),
            "INIT_Q4":
            random.randint(0, 1),
            "SRVAL_Q1":
            random.randint(0, 1),
            "SRVAL_Q2":
            random.randint(0, 1),
            "SRVAL_Q3":
            random.randint(0, 1),
            "SRVAL_Q4":
            random.randint(0, 1),
            "NUM_CE":
            random.randint(1, 2),
            # The following one shows negative correlation (0 - not inverted)
            "IS_D_INVERTED":
            random.randint(0, 1),
            # No bits were found for parameters below
            #"IS_OCLKB_INVERTED": random.randint(0, 1),
            #"IS_OCLK_INVERTED": random.randint(0, 1),
            #"IS_CLKDIVP_INVERTED": random.randint(0, 1),
            #"IS_CLKDIV_INVERTED": random.randint(0, 1),
            #"IS_CLKB_INVERTED": random.randint(0, 1),
            #"IS_CLK_INVERTED": random.randint(0, 1),
            "DYN_CLKDIV_INV_EN":
            verilog.quote(random.choice(["TRUE", "FALSE"])),
            "DYN_CLK_INV_EN":
            verilog.quote(random.choice(["TRUE", "FALSE"])),
            "IOBDELAY":
            verilog.quote(random.choice(["NONE", "IBUF", "IFD", "BOTH"])),
            "OFB_USED":
            verilog.quote(
                random.choice(["TRUE"] + ["FALSE"] * 9)),  # Force more FALSEs
        }

        iface_type = random.choice(
            [
                "NETWORKING", "OVERSAMPLE", "MEMORY", "MEMORY_DDR3",
                "MEMORY_QDR"
            ])
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

        # Instantiate cell
        param_str = ",".join(".%s(%s)" % (k, v) for k, v in params.items())

        print('')
        print('(* LOC="%s", KEEP, DONT_TOUCH *)' % iob_i)
        print('IBUF ibuf_%03d (.I(di[%3d]), .O(di_buf[%3d]));' % (i, i, i))
        print('(* LOC="%s", KEEP, DONT_TOUCH *)' % iob_o)
        print('OBUF obuf_%03d (.I(do_buf[%3d]), .O(do[%3d]));' % (i, i, i))
        print(
            'iserdes_single #(%s) iserdes_%03d (.clk1(clk1), .clk2(clk2), .I(di_buf[%3d]), .O(do_buf[%3d]));'
            % (param_str, i, i, i))

        params["TILE"] = tile_name
        data.append(params)

    # Store params
    with open("params.json", "w") as fp:
        json.dump(data, fp, sort_keys=True, indent=1)

    print(
        '''
endmodule

(* KEEP, DONT_TOUCH *)
module iserdes_single(
  input  wire clk1,
  input  wire clk2,
  input  wire I,
  output wire O
);

parameter _LOC = "";
parameter IS_USED = 1;
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

(* KEEP, DONT_TOUCH *)
wire [7:0] x;

generate if (IS_USED) begin

  // Single ISERDES
  (* LOC=_LOC, KEEP, DONT_TOUCH *)
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
  .DYNCLKDIVSEL(),
  .CLKDIV(),
  .CLKDIVP(),
  .RST(),
  .BITSLIP(),
  .O(),
  .Q1(x[0]),
  .Q2(x[1]),
  .Q3(x[2]),
  .Q4(x[3]),
  .Q5(x[4]),
  .Q6(x[5]),
  .Q7(x[6]),
  .Q8(x[7]),
  .SHIFTOUT1(),
  .SHIFTOUT2()
  );

end else begin

  assign x[0] = I;
  assign x[1] = I;
  assign x[2] = I;
  assign x[3] = I;
  assign x[4] = I;
  assign x[5] = I;
  assign x[6] = I;
  assign x[7] = I;

end endgenerate

// Output
assign O = |x;

endmodule
    ''')


run()
