import os
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray.db import Database


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        if gridinfo.tile_type in ['CLBLL_L', 'CLBLL_R', 'CLBLM_L', 'CLBLM_R']:
            site_name = sorted(gridinfo.sites.keys())[0]
            if gridinfo.tile_type[-1] == 'L':
                int_tile_loc = (loc.grid_x + 1, loc.grid_y)
            else:
                int_tile_loc = (loc.grid_x - 1, loc.grid_y)

            int_tile_name = grid.tilename_at_loc(int_tile_loc)

            if not int_tile_name.startswith('INT_'):
                continue

            yield int_tile_name, site_name


def write_params(params):
    pinstr = 'tile,val\n'
    for tile, (site, val) in sorted(params.items()):
        pinstr += '%s,%s,%s\n' % (tile, val, site)
    open('params.csv', 'w').write(pinstr)


def run():
    print('''
module top();
    ''')

    params = {}

    sites = sorted(list(gen_sites()))
    for (tile_name, site_name), isone in zip(sites,
                                             util.gen_fuzz_states(len(sites))):
        params[tile_name] = (site_name, isone)

        # Force HARD0 -> GFAN1 with I2 = 0
        # Toggle 1 pip with I1 = ?
        print(
            '''
            wire lut_to_f7_{0}, f7_to_f8_{0};
            (* KEEP, DONT_TOUCH, LOC = "{0}" *)
            LUT6_L #(
            .INIT(0)
            ) lut_rom_{0} (
                    .I0(1),
                    .I1({1}),
                    .I2(0),
                    .I3(1),
                    .I4(1),
                    .I5(1),
                    .LO(lut_to_f7_{0})
                    );
            (* KEEP, DONT_TOUCH, LOC = "{0}" *)
            MUXF7_L f7_{0} (
                .I0(lut_to_f7_{0}),
                .LO(f7_to_f8_{0})
                );
            (* KEEP, DONT_TOUCH, LOC = "{0}" *)
            MUXF8 f8_{0} (
                .I0(f7_to_f8_{0})
                );
'''.format(site_name, isone))

    print("endmodule")
    write_params(params)


if __name__ == '__main__':
    run()
