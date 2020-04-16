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
import math
import os
import functools
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import verilog
from prjxray.verilog import vrandbits
from prjxray.db import Database


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        if gridinfo.tile_type not in ['BRAM_L', 'BRAM_R']:
            continue

        sites = {}
        for site_name, site_type in gridinfo.sites.items():
            sites[site_type] = site_name

        yield tile_name, sites


@functools.lru_cache(maxsize=None)
def prepare_rand_int_choices(minval, maxval):
    """ Creates list ints between minval and maxval to allow fuzzer to uniquely identify all bits."""
    assert minval >= 0
    assert maxval >= minval

    min_p2 = math.floor(math.log(max(minval, 1), 2))
    max_p2 = math.ceil(math.log(maxval + 1, 2))

    if 2**max_p2 > maxval:
        max_search_p2 = max_p2 - 1
    else:
        max_search_p2 = max_p2

    choices = set(
        [minval, maxval, 2**(min_p2 + 1) - 1, 2**(max_search_p2) - 1])

    lb = min_p2
    ub = max_search_p2

    while lb < ub:
        ub = int(round(ub / 2.))

        val = 2**ub - 1

        lowval = val
        if lowval < minval:
            lowval |= (1 << max_search_p2)
        assert lowval >= minval, (val, ub)
        choices.add(lowval)

        highval = val << (max_search_p2 - ub)
        if highval > minval:
            assert highval <= maxval, (val, ub)
            choices.add(highval)

    for bit in range(max_search_p2):
        if 2**bit > minval:
            choices.add(2**bit)
        else:
            choices.add(2**bit | 2**max_search_p2)
            choices.add(2**bit | 2**(max_search_p2 - 1))

    zeros = set()
    ones = set()

    for choice in choices:
        assert choice >= minval, choice
        assert choice <= maxval, choice

        for bit in range(max_p2):
            if (1 << bit) & choice:
                ones.add(bit)
            else:
                zeros.add(bit)

    assert len(ones) == max_p2
    assert len(zeros) == max_p2

    return tuple(sorted(choices))


def rand_int(minval, maxval):
    return random.choice(prepare_rand_int_choices(minval, maxval))


def main():
    print('''
module top();
    ''')

    params_list = []
    for tile_name, sites in gen_sites():
        params = {}
        params['tile'] = tile_name
        params['site'] = sites['RAMBFIFO36E1']

        params['DATA_WIDTH'] = random.choice([4, 9, 18, 36, 72])
        params['EN_SYN'] = random.randint(0, 1)
        params['DO_REG'] = 1
        if params['EN_SYN']:
            params['FIRST_WORD_FALL_THROUGH'] = 0
        else:
            params['FIRST_WORD_FALL_THROUGH'] = random.randint(0, 1)

        if params['EN_SYN']:
            MIN_ALMOST_FULL_OFFSET = 1
            if params['DATA_WIDTH'] == 4:
                MAX_ALMOST_FULL_OFFSET = 8190
            elif params['DATA_WIDTH'] == 9:
                MAX_ALMOST_FULL_OFFSET = 4094
            elif params['DATA_WIDTH'] == 18:
                MAX_ALMOST_FULL_OFFSET = 2046
            elif params['DATA_WIDTH'] == 36:
                MAX_ALMOST_FULL_OFFSET = 1022
            elif params['DATA_WIDTH'] == 72:
                MAX_ALMOST_FULL_OFFSET = 510
            else:
                assert False

            MIN_ALMOST_EMPTY_OFFSET = MIN_ALMOST_FULL_OFFSET
            MAX_ALMOST_EMPTY_OFFSET = MAX_ALMOST_FULL_OFFSET
        else:
            MIN_ALMOST_FULL_OFFSET = 4
            if params['DATA_WIDTH'] == 4:
                MAX_ALMOST_FULL_OFFSET = 8185
            elif params['DATA_WIDTH'] == 9:
                MAX_ALMOST_FULL_OFFSET = 4089
            elif params['DATA_WIDTH'] == 18:
                MAX_ALMOST_FULL_OFFSET = 2041
            elif params['DATA_WIDTH'] == 36:
                MAX_ALMOST_FULL_OFFSET = 1017
            elif params['DATA_WIDTH'] == 72:
                MAX_ALMOST_FULL_OFFSET = 505
            else:
                assert False

            if params['FIRST_WORD_FALL_THROUGH']:
                MIN_ALMOST_EMPTY_OFFSET = MIN_ALMOST_FULL_OFFSET + 2
                MAX_ALMOST_EMPTY_OFFSET = MAX_ALMOST_FULL_OFFSET + 2
            else:
                MIN_ALMOST_EMPTY_OFFSET = MIN_ALMOST_FULL_OFFSET + 1
                MAX_ALMOST_EMPTY_OFFSET = MAX_ALMOST_FULL_OFFSET + 1

        ALMOST_EMPTY_OFFSET = rand_int(
            MIN_ALMOST_EMPTY_OFFSET, MAX_ALMOST_EMPTY_OFFSET)
        ALMOST_FULL_OFFSET = rand_int(
            MIN_ALMOST_FULL_OFFSET, MAX_ALMOST_FULL_OFFSET)
        params['ALMOST_EMPTY_OFFSET'] = "13'b{:013b}".format(
            ALMOST_EMPTY_OFFSET)
        params['ALMOST_FULL_OFFSET'] = "13'b{:013b}".format(ALMOST_FULL_OFFSET)

        if params['DATA_WIDTH'] == 36:
            params['FIFO_MODE'] = verilog.quote('FIFO36_72')
        else:
            params['FIFO_MODE'] = verilog.quote(
                'FIFO36_72'
            )  #verilog.quote('FIFO18') #verilog.quote(random.choice(('FIFO18', 'FIFO18_36')))

        params['INIT'] = '0'  #vrandbits(36)
        params['SRVAL'] = '0'  #vrandbits(36)

        print(
            '''
            (* KEEP, DONT_TOUCH, LOC = "{site}" *)
            FIFO36E1 #(
                .ALMOST_EMPTY_OFFSET({ALMOST_EMPTY_OFFSET}),
                .ALMOST_FULL_OFFSET({ALMOST_FULL_OFFSET}),
                .DATA_WIDTH({DATA_WIDTH}),
                .DO_REG({DO_REG}),
                .EN_SYN({EN_SYN}),
                .FIFO_MODE({FIFO_MODE}),
                .FIRST_WORD_FALL_THROUGH({FIRST_WORD_FALL_THROUGH}),
                .INIT({INIT}),
                .SRVAL({SRVAL})
                ) fifo_{site} (
                );
            '''.format(**params, ))

        params['FIFO_MODE'] = verilog.unquote(params['FIFO_MODE'])

        params_list.append(params)

    print("endmodule")

    with open('params.json', 'w') as f:
        json.dump(params_list, f, indent=2)


if __name__ == '__main__':
    main()
