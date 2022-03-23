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

from prjxray.segmaker import Segmaker
from prjxray import util
from prjxray import verilog

iface_types = [
    "NETWORKING", "OVERSAMPLE", "MEMORY", "MEMORY_DDR3", "MEMORY_QDR"
]

data_rates = ["SDR", "DDR"]

data_widths = {
    "SDR": [2, 3, 4, 5, 6, 7, 8],
    "DDR": [4, 6, 8, 10, 14],
}


def run():

    segmk = Segmaker("design.bits")

    # Load tags
    with open("params.json", "r") as fp:
        data = json.load(fp)

    loc_to_tile_site_map = {}

    # Output tags
    for param_list in data:
        for params in param_list:
            loc = verilog.unquote(params["SITE_LOC"])

            get_xy = util.create_xy_fun('IOB_')
            x, y = get_xy(loc.replace("ILOGIC", "IOB"))

            loc_to_tile_site_map[loc] = params["TILE_NAME"] + ".IOB_Y%d" % (
                y % 2)

            # Site not used at all
            if not params["IS_USED"]:

                segmk.add_site_tag(loc, "ISERDES.SHIFTOUT_USED", 0)

                segmk.add_site_tag(loc, "IDDR_OR_ISERDES.IN_USE", 0)
                segmk.add_site_tag(loc, "ISERDES.IN_USE", 0)
                segmk.add_site_tag(loc, "IDDR.IN_USE", 0)

                segmk.add_site_tag(loc, "ISERDES.MODE.MASTER", 0)
                segmk.add_site_tag(loc, "ISERDES.MODE.SLAVE", 0)

                for i in iface_types:
                    if i == "NETWORKING":
                        for j in data_rates:
                            for k in data_widths[j]:
                                tag = "ISERDES.%s.%s.W%s" % (i, j, k)
                                segmk.add_site_tag(loc, tag, 0)
                    else:
                        segmk.add_site_tag(loc, "ISERDES.%s.DDR.W4" % i, 0)

                segmk.add_site_tag(loc, "ISERDES.NUM_CE.N1", 0)
                segmk.add_site_tag(loc, "ISERDES.NUM_CE.N2", 0)

                for i in range(1, 4 + 1):
                    segmk.add_site_tag(loc, "IFF.ZINIT_Q%d" % i, 0)

                for i in range(1, 4 + 1):
                    segmk.add_site_tag(loc, "IFF.ZSRVAL_Q%d" % i, 0)

    #            segmk.add_site_tag(loc, "ISERDES.IS_CLKB_INVERTED", 0)
    #            segmk.add_site_tag(loc, "ISERDES.IS_CLK_INVERTED", 1)

                segmk.add_site_tag(loc, "ISERDES.DYN_CLKDIV_INV_EN", 0)
                segmk.add_site_tag(loc, "ISERDES.DYN_CLK_INV_EN", 0)

                segmk.add_site_tag(loc, "IFFDELMUXE3.P0", 0)
                segmk.add_site_tag(loc, "IFFDELMUXE3.P1", 1)
                segmk.add_site_tag(loc, "IDELMUXE3.P0", 0)
                segmk.add_site_tag(loc, "IDELMUXE3.P1", 1)

                segmk.add_site_tag(loc, "ISERDES.OFB_USED", 0)

            # Site used as ISERDESE2
            elif verilog.unquote(params["BEL_TYPE"]) == "ISERDESE2":

                segmk.add_site_tag(loc, "IDDR_OR_ISERDES.IN_USE", 1)
                segmk.add_site_tag(loc, "ISERDES.IN_USE", 1)

                if "SHIFTOUT_USED" in params:
                    if params["CHAINED"]:
                        value = params["SHIFTOUT_USED"]
                        segmk.add_site_tag(loc, "ISERDES.SHIFTOUT_USED", value)

                if "SERDES_MODE" in params:
                    value = verilog.unquote(params["SERDES_MODE"])
                    if value == "MASTER":
                        segmk.add_site_tag(loc, "ISERDES.MODE.MASTER", 1)
                        segmk.add_site_tag(loc, "ISERDES.MODE.SLAVE", 0)
                    if value == "SLAVE":
                        segmk.add_site_tag(loc, "ISERDES.MODE.MASTER", 0)
                        segmk.add_site_tag(loc, "ISERDES.MODE.SLAVE", 1)

                iface_type = verilog.unquote(params["INTERFACE_TYPE"])
                data_rate = verilog.unquote(params["DATA_RATE"])
                data_width = int(params["DATA_WIDTH"])

                for i in iface_types:
                    if i == "NETWORKING":
                        for j in data_rates:
                            for k in data_widths[j]:
                                tag = "ISERDES.%s.%s.W%s" % (i, j, k)

                                if i == iface_type:
                                    if j == data_rate:
                                        if k == data_width:
                                            segmk.add_site_tag(loc, tag, 1)
                    else:
                        if i == iface_type:
                            segmk.add_site_tag(loc, "ISERDES.%s.DDR.W4" % i, 1)

                if "NUM_CE" in params:
                    value = params["NUM_CE"]
                    if value == 1:
                        segmk.add_site_tag(loc, "ISERDES.NUM_CE.N1", 1)
                        segmk.add_site_tag(loc, "ISERDES.NUM_CE.N2", 0)
                    if value == 2:
                        segmk.add_site_tag(loc, "ISERDES.NUM_CE.N1", 0)
                        segmk.add_site_tag(loc, "ISERDES.NUM_CE.N2", 1)

                for i in range(1, 4 + 1):
                    if ("INIT_Q%d" % i) in params:
                        segmk.add_site_tag(
                            loc, "IFF.ZINIT_Q%d" % i,
                            not params["INIT_Q%d" % i])

                for i in range(1, 4 + 1):
                    if ("SRVAL_Q%d" % i) in params:
                        segmk.add_site_tag(
                            loc, "IFF.ZSRVAL_Q%d" % i,
                            not params["SRVAL_Q%d" % i])

                for inv in ["CLK", "CLKB", "OCLK", "OCLKB", "CLKDIV",
                            "CLKDIVP"]:
                    if "IS_{}_INVERTED".format(inv) in params:
                        segmk.add_site_tag(
                            loc, "ISERDES.INV_{}".format(inv),
                            params["IS_{}_INVERTED".format(inv)])
                        segmk.add_site_tag(
                            loc, "ISERDES.ZINV_{}".format(inv),
                            not params["IS_{}_INVERTED".format(inv)])

                if "DYN_CLKDIV_INV_EN" in params:
                    value = verilog.unquote(params["DYN_CLKDIV_INV_EN"])
                    segmk.add_site_tag(
                        loc, "ISERDES.DYN_CLKDIV_INV_EN", int(value == "TRUE"))
                if "DYN_CLK_INV_EN" in params:
                    value = verilog.unquote(params["DYN_CLK_INV_EN"])
                    segmk.add_site_tag(
                        loc, "ISERDES.DYN_CLK_INV_EN", int(value == "TRUE"))

                # This parameter actually controls muxes used both in ILOGIC and
                # ISERDES mode.
                if "IOBDELAY" in params:
                    value = verilog.unquote(params["IOBDELAY"])
                    if value == "NONE":
                        segmk.add_site_tag(loc, "IFFDELMUXE3.P0", 0)
                        segmk.add_site_tag(loc, "IFFDELMUXE3.P1", 1)
                        segmk.add_site_tag(loc, "IDELMUXE3.P0", 0)
                        segmk.add_site_tag(loc, "IDELMUXE3.P1", 1)
                    if value == "IBUF":
                        segmk.add_site_tag(loc, "IFFDELMUXE3.P0", 0)
                        segmk.add_site_tag(loc, "IFFDELMUXE3.P1", 1)
                        segmk.add_site_tag(loc, "IDELMUXE3.P0", 1)
                        segmk.add_site_tag(loc, "IDELMUXE3.P1", 0)
                    if value == "IFD":
                        segmk.add_site_tag(loc, "IFFDELMUXE3.P0", 1)
                        segmk.add_site_tag(loc, "IFFDELMUXE3.P1", 0)
                        segmk.add_site_tag(loc, "IDELMUXE3.P0", 0)
                        segmk.add_site_tag(loc, "IDELMUXE3.P1", 1)
                    if value == "BOTH":
                        segmk.add_site_tag(loc, "IFFDELMUXE3.P0", 1)
                        segmk.add_site_tag(loc, "IFFDELMUXE3.P1", 0)
                        segmk.add_site_tag(loc, "IDELMUXE3.P0", 1)
                        segmk.add_site_tag(loc, "IDELMUXE3.P1", 0)

                if "OFB_USED" in params:
                    value = verilog.unquote(params["OFB_USED"])
                    segmk.add_site_tag(
                        loc, "ISERDES.OFB_USED", int(value == "TRUE"))

            # Site used as IDDR
            elif verilog.unquote(params["BEL_TYPE"]) in ["IDDR",
                                                         "IDDR_NO_CLK"]:
                segmk.add_site_tag(loc, "IDDR_OR_ISERDES.IN_USE", 1)
                segmk.add_site_tag(loc, "IDDR.IN_USE", 1)
                segmk.add_site_tag(loc, "ISERDES.IN_USE", 0)

                if "DDR_CLK_EDGE" in params:
                    value = verilog.unquote(params["DDR_CLK_EDGE"])
                    segmk.add_site_tag(
                        loc, "IFF.DDR_CLK_EDGE.OPPOSITE_EDGE",
                        int(value == "OPPOSITE_EDGE"))
                    segmk.add_site_tag(
                        loc, "IFF.DDR_CLK_EDGE.SAME_EDGE",
                        int(value == "SAME_EDGE"))
                    segmk.add_site_tag(
                        loc, "IFF.DDR_CLK_EDGE.SAME_EDGE_PIPELINED",
                        int(value == "SAME_EDGE_PIPELINED"))

                if "SRTYPE" in params:
                    value = verilog.unquote(params["SRTYPE"])
                    if value == "ASYNC":
                        segmk.add_site_tag(loc, "IFF.SRTYPE.ASYNC", 1)
                        segmk.add_site_tag(loc, "IFF.SRTYPE.SYNC", 0)
                    if value == "SYNC":
                        segmk.add_site_tag(loc, "IFF.SRTYPE.ASYNC", 0)
                        segmk.add_site_tag(loc, "IFF.SRTYPE.SYNC", 1)

                if "IDELMUX" in params:
                    if params["IDELMUX"] == 1:
                        segmk.add_site_tag(loc, "IDELMUXE3.P0", 1)
                        segmk.add_site_tag(loc, "IDELMUXE3.P1", 0)
                    else:
                        segmk.add_site_tag(loc, "IDELMUXE3.P0", 0)
                        segmk.add_site_tag(loc, "IDELMUXE3.P1", 1)

                if "IFFDELMUX" in params:
                    if params["IFFDELMUX"] == 1:
                        segmk.add_site_tag(loc, "IFFDELMUXE3.P0", 1)
                        segmk.add_site_tag(loc, "IFFDELMUXE3.P1", 0)
                    else:
                        segmk.add_site_tag(loc, "IFFDELMUXE3.P0", 0)
                        segmk.add_site_tag(loc, "IFFDELMUXE3.P1", 1)

                for inv in ["C", "D"]:
                    if "IS_{}_INVERTED".format(inv) in params:
                        segmk.add_site_tag(
                            loc, "INV_{}".format(inv),
                            params["IS_{}_INVERTED".format(inv)])
                        segmk.add_site_tag(
                            loc, "ZINV_{}".format(inv),
                            not params["IS_{}_INVERTED".format(inv)])

                segmk.add_site_tag(loc, "ISERDES.NUM_CE.N1", 1)
                segmk.add_site_tag(loc, "ISERDES.NUM_CE.N2", 0)

            # Should not happen
            else:
                print("Unknown BEL_TYPE '{}'".format(params["BEL_TYPE"]))
                exit(-1)

    # Write segments and tags for later check
    def_tags = {t: 0 for d in segmk.site_tags.values() for t in d.keys()}

    with open("tags.json", "w") as fp:
        tags = {}
        for l, d in segmk.site_tags.items():
            d1 = dict(def_tags)
            d1.update({k: int(v) for k, v in d.items()})
            tags[loc_to_tile_site_map[l]] = d1

        json.dump(tags, fp, sort_keys=True, indent=1)

    def bitfilter(frame_idx, bit_idx):
        if frame_idx < 26 or frame_idx > 29:
            return False
        return True

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


if __name__ == "__main__":
    run()
