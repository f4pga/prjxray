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
                x, y = xy_fun(site)
                xs.append(x)
                ys.append(y)

                sites.append((site, x, y))

        if sites:
            yield tile_name, min(xs), min(ys), sorted(sites)

class StateGen(object):
    def __init__(self, sites, states_per_site):
        self.sites = sites
        self.states_per_site = states_per_site
        self.curr_site_idx = 0
        self.curr_state = None
        self.states = None
        self.curr_site = None

    def __iter__(self):
        assert self.curr_state is None
        assert self.states is None
        assert self.curr_state is None

        self.curr_site_idx = 0
        self.curr_state = None
        self.states = util.gen_fuzz_states(len(self.sites)*self.states_per_site)
        self.curr_site = iter(self.sites)
        return self

    def __next__(self):
        next_site = next(self.curr_site)
        self.curr_site_idx += 1

        if self.curr_state is not None:
            while self.curr_state < self.states_per_site:
                self.next_state()

            assert self.curr_state == self.states_per_site, self.curr_state

        self.curr_state = 0

        return next_site

    def next_state(self):
        self.curr_state += 1

        try:
            state = next(self.states)
        except StopIteration:
            assert False, "Insufficent states, at state {} for site {}".format(self.curr_state, self.curr_site_idx)

        return state


def main():
    print('''
module top();
    ''')

    params_list = []
    state_gen = StateGen(list(gen_sites()), states_per_site=12*16)
    for tile_name, x_min, y_min, sites in state_gen:
        for site, x, y in sites:
            params = {}
            params['tile'] = tile_name
            params['site'] = site
            params['x'] = x - x_min
            params['y'] = y - y_min
            params['IN_USE'] = state_gen.next_state()

            if params['IN_USE']:
                params['INIT_OUT'] = state_gen.next_state()
                params['IS_CE0_INVERTED'] = state_gen.next_state()
                params['IS_CE1_INVERTED'] = state_gen.next_state()
                params['IS_S0_INVERTED'] = state_gen.next_state()
                params['IS_S1_INVERTED'] = state_gen.next_state()
                params['IS_IGNORE0_INVERTED'] = state_gen.next_state()
                params['IS_IGNORE1_INVERTED'] = state_gen.next_state()

                params['PRESELECT_I0'] = state_gen.next_state()
                if not params['PRESELECT_I0']:
                    params['PRESELECT_I1'] = state_gen.next_state()
                else:
                    params['PRESELECT_I1'] = 0

                params['force_0_high'] = state_gen.next_state()
                params['force_1_high'] = state_gen.next_state()
                if params['force_0_high']:
                    params['force_1_high'] = 0

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
            .CE0(ce0_{site} | {force_0_high}),
            .S0(s0_{site} | {force_0_high}),
            .CE1(ce1_{site} | {force_1_high}),
            .S1(s1_{site} | {force_1_high})
        );
                    '''.format(**params))

            params_list.append(params)

    print("""
    (* KEEP, DONT_TOUCH *)
    LUT6 dummy (
        );""")

    print("endmodule")

    with open('params.json', 'w') as f:
        json.dump(params_list, f, indent=2)


if __name__ == '__main__':
    main()
