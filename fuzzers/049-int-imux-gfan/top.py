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
import os
import random
import itertools
from prjxray import util
from prjxray.db import Database
random.seed(int(os.getenv("SEED"), 16))


def gen_sites(lr):
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    for tile_name in grid.tiles():
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        if gridinfo.tile_type[-1] != lr:
            continue

        sites = []
        for site_name, site_type in gridinfo.sites.items():
            if site_type in ['SLICEL', 'SLICEM']:
                sites.append(site_name)

        if not sites:
            continue

        print('// ', gridinfo.tile_type)

        yield sorted(sites)


def yield_bits(bits, nvals):
    for i in range(nvals):
        mask = (1 << i)
        yield int(bool(bits & mask))


NUM_IMUX_INPUTS = 2 * 6 * 4
NUM_TILES = 20


def emit_luts(choices, spec_idx, lr):
    for idx, sites in enumerate(itertools.islice(gen_sites(lr), 0, NUM_TILES)):

        cidx = idx + spec_idx * NUM_TILES
        if cidx < len(choices):
            bits = choices[cidx]
        else:
            bits = random.randint(0, 2**NUM_IMUX_INPUTS - 1)

        itr = yield_bits(bits, nvals=NUM_IMUX_INPUTS)

        for site in sites:
            for lut in range(4):
                print(
                    '''
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    LUT6 {site}_lut{lut} (
        .I0({I0}),
        .I1({I1}),
        .I2({I2}),
        .I3({I3}),
        .I4({I4}),
        .I5({I5})
        );'''.format(
                        site=site,
                        lut=lut,
                        I0=next(itr),
                        I1=next(itr),
                        I2=next(itr),
                        I3=next(itr),
                        I4=next(itr),
                        I5=next(itr),
                    ))


def run():

    print('''
module top();
''')

    choices = util.gen_fuzz_choices(nvals=NUM_IMUX_INPUTS)
    spec_idx = util.specn() - 1

    emit_luts(choices, spec_idx, 'L')
    emit_luts(choices, spec_idx, 'R')

    print("endmodule")


if __name__ == '__main__':
    run()
