import os
import random
#random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray.db import Database


def gen_sites():
    db = Database(util.get_db_root())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        if gridinfo.tile_type in ['CFG_CENTER_MID']:
            for site_name in sorted(gridinfo.sites.keys()):
                if site_name.startswith("BSCAN_X0Y0"):
                    yield tile_name, site_name


def write_params(params):
    pinstr = 'tile,val,site\n'
    for tile, (site, val) in sorted(params.items()):
        pinstr += '%s,%s,%s\n' % (tile, val, site)
    open('params.csv', 'w').write(pinstr)


def run():
    print('''
module top();
    ''')
    params = {}

    sites = list(gen_sites())
    jtag_chains = ("1", "2", "3", "4")
    for (tile_name, site_name), isone in zip(sites,
                                             util.gen_fuzz_states(len(sites))):
        site_name = site_name[:-1]
        site_name = site_name + str(isone)
        params[tile_name] = (site_name, isone)
        print(
            '''
            (* KEEP, DONT_TOUCH, LOC = "{0}" *)
            BSCANE2 #(
            .JTAG_CHAIN("{1}")
            )
            BSCANE2_{0} (
            .CAPTURE(),
            .DRCK(),
            .RESET(),
            .RUNTEST(),
            .SEL(),
            .SHIFT(),
            .TCK(),
            .TDI(),
            .TMS(),
            .UPDATE(),
            .TDO(1'b1)
            );
        '''.format(site_name, jtag_chains[isone]))

    print("endmodule")
    write_params(params)


if __name__ == '__main__':
    run()
