import json
import io
import os
import random
import re
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import lut_maker
from prjxray import verilog
from prjxray.db import Database


def gen_sites():
    db = Database(util.get_db_root())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        if gridinfo.tile_type.endswith("_SING"):
            continue

        sites = []
        for site_name, site_type in gridinfo.sites.items():
            if site_type == 'IDELAYE2':
                sites.append(site_name)

        if len(sites) == 0:
            continue

        sites_y = [
            int(re.match('IDELAY_X[0-9]+Y([0-9]+)', site).group(1))
            for site in sites
        ]
        sites, _ = zip(*sorted(zip(sites, sites_y), key=lambda x: x[1]))

        if gridinfo.tile_type[0] == 'L':
            pad_grid_x = loc.grid_x - 1
        else:
            pad_grid_x = loc.grid_x + 1

        pad_gridinfo = grid.gridinfo_at_loc((pad_grid_x, loc.grid_y))
        pad_sites = pad_gridinfo.sites.keys()
        pad_sites_y = [
            int(re.match('IOB_X[0-9]+Y([0-9]+)', site).group(1))
            for site in pad_sites
        ]
        pad_sites, _ = zip(
            *sorted(zip(pad_sites, pad_sites_y), key=lambda x: x[1]))
        assert len(sites) == len(pad_sites), (sites, pad_sites)
        for site_name, pad_site in zip(sites, pad_sites):
            yield tile_name, site_name, pad_site


def write_params(params):
    pinstr = 'tile,isone,site,pin\n'
    for vals in params:
        pinstr += ','.join(map(str, vals)) + '\n'

    open('params.csv', 'w').write(pinstr)


def use_idelay(p, luts, connects):
    print(
        '''
    wire idelay_{site};

    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    IDELAYE2 #(
    ) idelay_site_{site} (
        .IDATAIN({iwire}),
        .DATAOUT(idelay_{site})
        );
    assign {owire} = {onet};
    assign {net} = idelay_{site};
       '''.format(
            onet=luts.get_next_output_net(),
            net=luts.get_next_input_net(),
            **p),
        file=connects)
    if p['isone']:
        print(
            '''
    (* KEEP, DONT_TOUCH *)
    PULLUP #(
    ) pullup_{site} (
        .O({iwire}));
        '''.format(**p),
            file=connects)


def run():
    luts = lut_maker.LutMaker()
    connects = io.StringIO()

    tile_params = []
    params = []
    sites = list(gen_sites())
    for idx, ((tile, site, pad), isone) in enumerate(zip(
            sites, util.gen_fuzz_states(len(sites)))):

        p = {}
        p['tile'] = tile
        p['site'] = site

        p['owire'] = 'do[{}]'.format(idx)
        p['iwire'] = 'di[{}]'.format(idx)
        p['isone'] = isone
        params.append(p)
        tile_params.append((tile, p['isone'], site, p['iwire'], pad))

    write_params(tile_params)

    print(
        '''
`define N_DI {n_di}

module top(input [`N_DI-1:0] di);
    wire [`N_DI-1:0] di;
    wire [`N_DI-1:0] do;
    '''.format(n_di=idx + 1))

    # Always output a LUT6 to make placer happy.
    print('''
     (* KEEP, DONT_TOUCH *)
     LUT6 dummy_lut();
     ''')

    # Need IDELAYCTRL for IDEALAYs
    print('''
     (* KEEP, DONT_TOUCH *)
     IDELAYCTRL();
     ''')

    for p in params:
        use_idelay(p, luts, connects)

    for l in luts.create_wires_and_luts():
        print(l)

    print(connects.getvalue())

    print("endmodule")


if __name__ == '__main__':
    run()
