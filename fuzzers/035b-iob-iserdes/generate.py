#!/usr/bin/env python3
import json
import re

from prjxray.segmaker import Segmaker
from prjxray import util
from prjxray import verilog

segmk = Segmaker("design.bits")

# Load tags
with open("params.json", "r") as fp:
    data = json.load(fp)

iface_types = [
    "NETWORKING", "OVERSAMPLE", "MEMORY", "MEMORY_DDR3", "MEMORY_QDR"
]
data_rates = ["SDR", "DDR"]
data_widths = [2, 3, 4, 5, 6, 7, 8, 10, 14]

# Output tags
#loc_to_tile_site_map = {}
for param_list in data:
    for params in param_list:
        loc = verilog.unquote(params["SITE_LOC"])
        loc = loc.replace("ILOGIC", "IOB")

        get_xy = util.create_xy_fun('IOB_')
        x, y = get_xy(loc)

        #loc_to_tile_site_map[loc] = params["TILE"] + ".IOB_X0Y%d" % (y % 2)

        # Serdes not used at all
        if not params["IS_USED"]:

            segmk.add_site_tag(loc, "ISERDES.SHIFTOUT_USED", 0)
            
            segmk.add_site_tag(loc, "ISERDES.IN_USE", 0)

            segmk.add_site_tag(loc, "ISERDES.MODE.MASTER", 0)
            segmk.add_site_tag(loc, "ISERDES.MODE.SLAVE", 0)

            for i in iface_types:
                if i == "NETWORKING":
                    for j in data_widths:
                        tag = "ISERDES.%s.%s" % (i, j)
                        segmk.add_site_tag(loc, tag, 0)
                else:
                    segmk.add_site_tag(loc, "ISERDES.%s.4" % i, 0)

            segmk.add_site_tag(loc, "ISERDES.NUM_CE.1", 0)
            segmk.add_site_tag(loc, "ISERDES.NUM_CE.2", 0)

            for i in range(1, 4 + 1):
                segmk.add_site_tag(loc, "IFF.ZINIT_Q%d" % i, 0)

            for i in range(1, 4 + 1):
                segmk.add_site_tag(loc, "IFF.ZSRVAL_Q%d" % i, 0)

            segmk.add_site_tag(loc, "ZINV_D", 0)

            segmk.add_site_tag(loc, "ISERDES.DYN_CLKDIV_INV_EN", 0)
            segmk.add_site_tag(loc, "ISERDES.DYN_CLK_INV_EN", 0)

            segmk.add_site_tag(loc, "IFFDELMUXE3.0", 1)
            segmk.add_site_tag(loc, "IFFDELMUXE3.1", 0)
            segmk.add_site_tag(loc, "IDELMUXE3.0", 1)
            segmk.add_site_tag(loc, "IDELMUXE3.1", 0)

            segmk.add_site_tag(loc, "ISERDES.OFB_USED", 0)

        # Serdes used
        else:

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

            segmk.add_site_tag(loc, "ISERDES.SDR", int(data_rate == "SDR"))
            segmk.add_site_tag(loc, "ISERDES.DDR", int(data_rate == "DDR"))

            for i in iface_types:
                for j in data_widths:
                    tag = "ISERDES.%s.%s" % (i, j)

                    if i == iface_type:
                        if j == data_width:
                            segmk.add_site_tag(loc, tag, 1)

            if "NUM_CE" in params:
                value = params["NUM_CE"]
                if value == 1:
                    segmk.add_site_tag(loc, "ISERDES.NUM_CE.1", 1)
                    segmk.add_site_tag(loc, "ISERDES.NUM_CE.2", 0)
                if value == 2:
                    segmk.add_site_tag(loc, "ISERDES.NUM_CE.1", 0)
                    segmk.add_site_tag(loc, "ISERDES.NUM_CE.2", 1)

            for i in range(1, 4 + 1):
                if ("INIT_Q%d" % i) in params:
                    segmk.add_site_tag(
                        loc, "IFF.ZINIT_Q%d" % i, not params["INIT_Q%d" % i])

            for i in range(1, 4 + 1):
                if ("SRVAL_Q%d" % i) in params:
                    segmk.add_site_tag(
                        loc, "IFF.ZSRVAL_Q%d" % i, not params["SRVAL_Q%d" % i])

            if "IS_D_INVERTED" in params:
                if not params["CHAINED"]:
                    segmk.add_site_tag(
                        loc, "ZINV_D", int(params["IS_D_INVERTED"] == 0))

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
                    #segmk.add_site_tag(loc, "IOBDELAY_NONE", 1)
                    segmk.add_site_tag(loc, "IFFDELMUXE3.0", 0)
                    segmk.add_site_tag(loc, "IFFDELMUXE3.1", 1)
                    segmk.add_site_tag(loc, "IDELMUXE3.0", 0)
                    segmk.add_site_tag(loc, "IDELMUXE3.1", 1)
                if value == "IBUF":
                    #segmk.add_site_tag(loc, "IOBDELAY_IBUF", 1)
                    segmk.add_site_tag(loc, "IFFDELMUXE3.0", 0)
                    segmk.add_site_tag(loc, "IFFDELMUXE3.1", 1)
                    segmk.add_site_tag(loc, "IDELMUXE3.0", 1)
                    segmk.add_site_tag(loc, "IDELMUXE3.1", 0)
                if value == "IFD":
                    #segmk.add_site_tag(loc, "IOBDELAY_IFD" , 1)
                    segmk.add_site_tag(loc, "IFFDELMUXE3.0", 1)
                    segmk.add_site_tag(loc, "IFFDELMUXE3.1", 0)
                    segmk.add_site_tag(loc, "IDELMUXE3.0", 0)
                    segmk.add_site_tag(loc, "IDELMUXE3.1", 1)
                if value == "BOTH":
                    #segmk.add_site_tag(loc, "IOBDELAY_BOTH", 1)
                    segmk.add_site_tag(loc, "IFFDELMUXE3.0", 1)
                    segmk.add_site_tag(loc, "IFFDELMUXE3.1", 0)
                    segmk.add_site_tag(loc, "IDELMUXE3.0", 1)
                    segmk.add_site_tag(loc, "IDELMUXE3.1", 0)

            if "OFB_USED" in params:
                value = verilog.unquote(params["OFB_USED"])
                if value == "TRUE":
                    segmk.add_site_tag(loc, "ISERDES.OFB_USED", 1)

# Write segments and tags for later check
#with open("tags.json", "w") as fp:
#    tags = {
#        loc_to_tile_site_map[l]: {k: int(v)
#                                  for k, v in d.items()}
#        for l, d in segmk.site_tags.items()
#    }
#    json.dump(tags, fp, sort_keys=True, indent=1)


def bitfilter(frame_idx, bit_idx):
    if frame_idx < 26 or frame_idx > 31:
        return False
    return True


segmk.compile(bitfilter=bitfilter)
segmk.write()
