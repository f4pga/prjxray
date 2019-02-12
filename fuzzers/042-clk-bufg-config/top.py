import json
import os
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray.db import Database


def gen_sites():
    xy_fun = util.create_xy_fun('BUFGCTRL_')
    db = Database(util.get_db_root())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        sites = []

        xs = []
        ys = []
        for site, site_type in gridinfo.sites.items():
            if site_type == 'BUFGCTRL':
                x, y = xy_fun()
                xs.append(x)
                ys.append(y)

                sites.append((site, x, y))

        if sites:
            yield tile_name, min(xs), min(ys), sorted(sites)


def main():
    print('''
module top();
    ''')

    params_list = []
    for tile_name, x_min, y_min, sites in gen_sites():

        for site, x, y in sites:
            params = {}
            params['tile'] = tile_name
            params['site'] = site
            params['x'] = x - x_min
            params['y'] = y - y_min
            params['IN_USE'] = random.random() > .1

            if params['IN_USE']:
                params['INIT_OUT'] = random.randint(0, 1)
                params['IS_CE0_INVERTED'] = random.randint(0, 1)
                params['IS_CE1_INVERTED'] = random.randint(0, 1)
                params['IS_S0_INVERTED'] = random.randint(0, 1)
                params['IS_S1_INVERTED'] = random.randint(0, 1)
                params['IS_IGNORE0_INVERTED'] = random.randint(0, 1)
                params['IS_IGNORE1_INVERTED'] = random.randint(0, 1)
                params['PRESELECT_I0'] = 0
                params['PRESELECT_I1'] = 0

                params['connect0'] = random.randint(0, 1)

                if params['connect0']:
                    params['connect1'] = random.randint(0, 1)
                else:
                    params['connect1'] = 1

                if params['connect0'] and params['connect1']:
                    params['PRESELECT_I0'] = random.randint(0, 1)
                    if not params['PRESELECT_I0']:
                        params['PRESELECT_I1'] = random.randint(0, 1)
                    else:
                        params['PRESELECT_I1'] = 0

                    params['connections'] = """
            .CE0(ce0_{site}),
            .S0(s0_{site}),
            .CE1(ce1_{site}),
            .S1(s1_{site})
                        """.format(site=site)
                elif params['connect0']:
                    params['connections'] = """
            .CE0(ce0_{site}),
            .S0(s0_{site})
                        """.format(site=site)
                elif params['connect1']:
                    params['connections'] = """
            .CE1(ce1_{site}),
            .S1(s1_{site})
                        """.format(site=site)



                print(
                    '''
    wire ce0_{site};
    wire s0_{site};
    (* KEEP, DONT_TOUCH *)
    LUT6 l0_{site} (
        .O(ce0_{site})
        );
    (* KEEP, DONT_TOUCH *)
    LUT6 l1_{site} (
        .O(s0_{site})
        );

    wire ce1_{site};
    wire s1_{site};
    (* KEEP, DONT_TOUCH *)
    LUT6 l2_{site} (
        .O(ce1_{site})
        );
    (* KEEP, DONT_TOUCH *)
    LUT6 l3_{site} (
        .O(s1_{site})
        );
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    BUFGCTRL #(
        .INIT_OUT({INIT_OUT}),
        .PRESELECT_I0({PRESELECT_I0}),
        .PRESELECT_I1({PRESELECT_I1}),
        .IS_CE0_INVERTED({IS_CE0_INVERTED}),
        .IS_CE1_INVERTED({IS_CE1_INVERTED}),
        .IS_S0_INVERTED({IS_S0_INVERTED}),
        .IS_S1_INVERTED({IS_S1_INVERTED}),
        .IS_IGNORE0_INVERTED({IS_IGNORE0_INVERTED}),
        .IS_IGNORE1_INVERTED({IS_IGNORE1_INVERTED})
        ) buf_{site} (
            {connections}
        );
                    '''.format(**params))

            params_list.append(params)

    print("endmodule")

    with open('params.json', 'w') as f:
        json.dump(params_list, f, indent=2)


if __name__ == '__main__':
    main()
