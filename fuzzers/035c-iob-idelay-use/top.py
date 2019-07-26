#!/usr/bin/env python3

import os, random
random.seed(int(os.getenv("SEED"), 16))

import re
import json

from prjxray import util
from prjxray.db import Database


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
        idelay_s = iob33s.replace("IOB", "IDELAY")
        idelay_m = iob33m.replace("IOB", "IDELAY")

        yield idelay_m, idelay_s


def run():

    # Get all [LR]IOI3 tiles
    tiles = list(gen_sites())

    # Header
    print("// Seed: '%s'" % os.getenv("SEED"))
    print('''module top ();
    IDELAYCTRL idelay_ctrl();''')

    # LOCes IOBs
    data = []
    for sites in tiles:

        if random.randint(0, 1):
            idelay = sites[0]
        else:
            idelay = sites[1]

        params = {}
        params["LOC"] = idelay

        if random.randint(0, 1):
            params["IN_USE"] = 1
            print(
                '''
    (* KEEP, DONT_TOUCH, LOC = "{idelay}" *)
    IDELAYE2 idelay_{idelay}();'''.format(idelay=idelay))
        else:
            params["IN_USE"] = 0

        data.append(params)

    print('endmodule')

    # Store params
    with open("params.json", "w") as fp:
        json.dump(data, fp, sort_keys=True, indent=1)


if __name__ == '__main__':
    run()
