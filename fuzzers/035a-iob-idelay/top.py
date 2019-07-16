#!/usr/bin/env python3

import os, random
random.seed(int(os.getenv("SEED"), 16))

import re
import json

from prjxray import util
from prjxray.db import Database

# =============================================================================


def get_loc(name):
    m = re.match("^\S+_X([0-9]+)Y([0-9]+)$", name)
    assert m != None

    x = int(m.group(1))
    y = int(m.group(2))
    return (
        x,
        y,
    )


def gen_sites():
    db = Database(util.get_db_root())
    grid = db.grid()

    tile_list = []
    for tile_name in sorted(grid.tiles()):
        if "IOB33" not in tile_name or "SING" in tile_name:
            continue
        tile_list.append(tile_name)

    def key(name):
        x, y = get_loc(name)
        return y + x * 10000

    tile_list.sort(key=key)

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

        #idelay = [k for k,v in ioi_gridinfo.sites.items() if v == "IDELAYE2"][0]
        iob33s = [k for k, v in iob_gridinfo.sites.items() if v == "IOB33S"][0]
        iob33m = [k for k, v in iob_gridinfo.sites.items() if v == "IOB33M"][0]
        idelay_s = iob33s.replace("IOB", "IDELAY")
        idelay_m = iob33m.replace("IOB", "IDELAY")

        yield iob33m, idelay_m, iob33s, idelay_s


def run():

    # Get all [LR]IOI3 tiles
    tiles = list(gen_sites())

    # Header
    print("// Tile count: %d" % len(tiles))
    print("// Seed: '%s'" % os.getenv("SEED"))
    print(
        '''
module top (
  input  wire [{N}:0] di,
  output wire [{N}:0] do
);

wire [{N}:0] di_buf;
wire [{N}:0] do_buf;
    '''.format(**{"N": len(tiles) - 1}))

    # LOCes IOBs
    data = []
    for i, sites in enumerate(tiles):

        if random.randint(0, 1):
            iob_i = sites[0]
            iob_o = sites[2]
            idelay = sites[1]
        else:
            iob_i = sites[2]
            iob_o = sites[0]
            idelay = sites[3]

        params = {
            "LOC":
            "\"" + idelay + "\"",
            "IDELAY_TYPE":
            "\"" + random.choice(
                ["FIXED", "VARIABLE", "VAR_LOAD", "VAR_LOAD_PIPE"]) + "\"",
            "IDELAY_VALUE":
            random.randint(0, 31),
            "DELAY_SRC":
            "\"" + random.choice(["IDATAIN", "DATAIN"]) + "\"",
            "HIGH_PERFORMANCE_MODE":
            "\"" + random.choice(["TRUE", "FALSE"]) + "\"",
            "CINVCTRL_SEL":
            "\"" + random.choice(["TRUE", "FALSE"]) + "\"",
            "PIPE_SEL":
            "\"" + random.choice(["TRUE", "FALSE"]) + "\"",
        }

        if params["IDELAY_TYPE"] != "\"VAR_LOAD_PIPE\"":
            params["PIPE_SEL"] = "\"FALSE\""

        # The datasheet says that for these two modes the delay is set to 0
        if params["IDELAY_TYPE"] == "\"VAR_LOAD\"":
            params["IDELAY_VALUE"] = 0
        if params["IDELAY_TYPE"] == "\"VAR_LOAD_PIPE\"":
            params["IDELAY_VALUE"] = 0

        # SIGNAL_PATTERN and HIGH_PERFORMANCE_MODE have no bits

        param_str = ",".join(".%s(%s)" % (k, v) for k, v in params.items())

        print('')
        print('(* LOC="%s", KEEP, DONT_TOUCH *)' % iob_i)
        print('IBUF ibuf_%03d (.I(di[%3d]), .O(di_buf[%3d]));' % (i, i, i))
        print('(* LOC="%s", KEEP, DONT_TOUCH *)' % iob_o)
        print('OBUF obuf_%03d (.I(do_buf[%3d]), .O(do[%3d]));' % (i, i, i))
        print(
            'mod #(%s) mod_%03d (.I(di_buf[%3d]), .O(do_buf[%3d]));' %
            (param_str, i, i, i))

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
  input  wire I,
  output wire O
);

parameter LOC = "";
parameter IDELAY_TYPE = "FIXED";
parameter IDELAY_VALUE = 0;
parameter DELAY_SRC = "IDATAIN";
parameter HIGH_PERFORMANCE_MODE = "TRUE";
parameter SIGNAL_PATTERN = "DATA";
parameter CINVCTRL_SEL = "FALSE";
parameter PIPE_SEL = "FALSE";

wire x;

// IDELAY
(* LOC=LOC, KEEP, DONT_TOUCH *)
IDELAYE2 #(
  .IDELAY_TYPE(IDELAY_TYPE),
  .IDELAY_VALUE(IDELAY_VALUE),
  .DELAY_SRC(DELAY_SRC),
  .HIGH_PERFORMANCE_MODE(HIGH_PERFORMANCE_MODE),
  .SIGNAL_PATTERN(SIGNAL_PATTERN),
  .CINVCTRL_SEL(CINVCTRL_SEL),
  .PIPE_SEL(PIPE_SEL)
)
idelay
(
  .C(),
  .REGRST(),
  .LD(),
  .CE(),
  .INC(),
  .CINVCTRL(),
  .CNTVALUEIN(),
  .IDATAIN(I),
  .DATAIN(),
  .LDPIPEEN(),
  .DATAOUT(x),
  .CNTVALUEOUT()
);

// A LUT
(* KEEP, DONT_TOUCH *)
LUT6 #(.INIT(32'hDEADBEEF)) lut (
  .I0(x),
  .I1(x),
  .I2(x),
  .I3(x),
  .I4(x),
  .I5(x),
  .O(O)
);

endmodule
    ''')


run()
