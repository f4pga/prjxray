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
import os
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import verilog
from prjxray.db import Database
from prjxray.lut_maker import LutMaker

WRITE_MODES = ("WRITE_FIRST", "NO_CHANGE", "READ_FIRST")


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


def ramb18(tile_name, luts, lines, sites):
    """ RAMB18E1 in either top or bottom site. """

    params = {}
    params['tile'] = tile_name
    params['Y0_IN_USE'] = random.randint(0, 1) == 1
    params['Y1_IN_USE'] = not params['Y0_IN_USE']
    params['FIFO_Y0_IN_USE'] = False
    params['FIFO_Y1_IN_USE'] = False

    if params['Y0_IN_USE']:
        site = sites['FIFO18E1']
    elif params['Y1_IN_USE']:
        site = sites['RAMB18E1']
    else:
        assert False

    lines.append(
        '''
        (* KEEP, DONT_TOUCH, LOC = "{site}" *)
        RAMB18E1 #(
            ) bram_{site} (
            );
        '''.format(site=site))

    return params


def ramb18_2x(tile_name, luts, lines, sites):
    """ RAMB18E1 in both top and bottom site. """

    params = {}
    params['tile'] = tile_name
    params['Y0_IN_USE'] = True
    params['Y1_IN_USE'] = True
    params['FIFO_Y0_IN_USE'] = False
    params['FIFO_Y1_IN_USE'] = False

    lines.append(
        '''
        (* KEEP, DONT_TOUCH, LOC = "{top_site}" *)
        RAMB18E1 #(
            ) bram_{top_site} (
            );
        (* KEEP, DONT_TOUCH, LOC = "{bottom_site}" *)
        RAMB18E1 #(
            ) bram_{bottom_site} (
            );
        '''.format(
            top_site=sites['FIFO18E1'],
            bottom_site=sites['RAMB18E1'],
        ))

    return params


def ramb36(tile_name, luts, lines, sites):
    """ RAMB36 consuming entire tile. """

    params = {}
    params['tile'] = tile_name
    params['Y0_IN_USE'] = True
    params['Y1_IN_USE'] = True
    params['FIFO_Y0_IN_USE'] = False
    params['FIFO_Y1_IN_USE'] = False

    site = sites['RAMBFIFO36E1']

    lines.append(
        """
        wire [7:0] webwe_{site};
        wire [3:0] wea_{site};
        wire regce_{site};
        wire [15:0] rdaddr_{site};
        wire [15:0] wraddr_{site};
        """.format(site=site))

    for bit in range(15):
        lines.append(
            'assign rdaddr_{site}[{bit}] = {net};'.format(
                bit=bit, site=site, net=luts.get_next_output_net()))
        lines.append(
            'assign wraddr_{site}[{bit}] = {net};'.format(
                bit=bit, site=site, net=luts.get_next_output_net()))

    for bit in range(8):
        lines.append(
            'assign webwe_{site}[{bit}] = {net};'.format(
                bit=bit, site=site, net=luts.get_next_output_net()))

    for bit in range(4):
        lines.append(
            'assign wea_{site}[{bit}] = {net};'.format(
                bit=bit, site=site, net=luts.get_next_output_net()))

    lines.append(
        'assign regce_{site} = {net};'.format(
            bit=bit, site=site, net=luts.get_next_output_net()))

    do_reg = verilog.vrandbit()
    ram_mode = random.choice(('SDP', 'TDP'))
    READ_WIDTH_A = 0
    READ_WIDTH_B = 0

    if ram_mode == 'TDP':
        write_mode_a = random.choice(WRITE_MODES)
        write_mode_b = random.choice(WRITE_MODES)
        WRITE_WIDTH_A = 36
        WRITE_WIDTH_B = 36
    else:
        write_mode_a = 'WRITE_FIRST'
        write_mode_b = 'WRITE_FIRST'
        WRITE_WIDTH_A = 72
        WRITE_WIDTH_B = 72

    lines.append(
        '''
        (* KEEP, DONT_TOUCH, LOC = "{site}" *)
        RAMB36E1 #(
            .DOA_REG({doa_reg}),
            .DOB_REG({dob_reg}),
            .WRITE_MODE_A({write_mode_a}),
            .WRITE_MODE_B({write_mode_b}),
            .READ_WIDTH_A({READ_WIDTH_A}),
            .READ_WIDTH_B({READ_WIDTH_B}),
            .WRITE_WIDTH_A({WRITE_WIDTH_A}),
            .WRITE_WIDTH_B({WRITE_WIDTH_B}),
            .INIT_A(36'hFF_FFFF_FFFF),
            .SRVAL_A(36'hFF_FFFF_FFFF),
            .INIT_B(36'hFF_FFFF_FFFF),
            .SRVAL_B(36'hFF_FFFF_FFFF),
            .RAM_MODE({ram_mode})
            ) bram_{site} (
                .ADDRARDADDR(rdaddr_{site}),
                .ADDRBWRADDR(wraddr_{site}),
                .REGCEAREGCE(regce_{site}),
                .REGCEB(regce_{site}),
                .WEBWE(webwe_{site}),
                .WEA(wea_{site})
            );
        '''.format(
            site=site,
            doa_reg=do_reg,
            dob_reg=do_reg,
            write_mode_a=verilog.quote(write_mode_a),
            write_mode_b=verilog.quote(write_mode_b),
            ram_mode=verilog.quote(ram_mode),
            READ_WIDTH_A=READ_WIDTH_A,
            READ_WIDTH_B=READ_WIDTH_B,
            WRITE_WIDTH_A=WRITE_WIDTH_A,
            WRITE_WIDTH_B=WRITE_WIDTH_B,
        ))

    return params


def fifo18(tile_name, luts, lines, sites):
    """ FIFO18E1 without bottom RAMB site. """

    params = {}
    params['tile'] = tile_name
    params['Y0_IN_USE'] = True
    params['Y1_IN_USE'] = False
    params['FIFO_Y0_IN_USE'] = True
    params['FIFO_Y1_IN_USE'] = False

    lines.append(
        '''
        wire fifo_rst_{site};
        (* KEEP, DONT_TOUCH *)
        LUT6 fifo_lut_{site} (
            .O(fifo_rst_{site})
            );

        (* KEEP, DONT_TOUCH, LOC = "{site}" *)
        FIFO18E1 #(
            .ALMOST_EMPTY_OFFSET(8),
            .ALMOST_FULL_OFFSET(8),
            .DATA_WIDTH({data_width})
            ) fifo_{site} (
                .RST(fifo_rst_{site})
            );
        '''.format(
            site=sites['FIFO18E1'],
            data_width=random.choice((4, 9)),
        ))

    return params


def fifo18_ramb18(tile_name, luts, lines, sites):
    """ FIFO18E1 in top site and RAMB18E1 in bottom site. """

    params = {}
    params['tile'] = tile_name
    params['Y0_IN_USE'] = True
    params['Y1_IN_USE'] = True
    params['FIFO_Y0_IN_USE'] = True
    params['FIFO_Y1_IN_USE'] = False

    lines.append(
        '''
        wire fifo_rst_{fifo_site};
        (* KEEP, DONT_TOUCH *)
        LUT6 fifo_lut_{fifo_site} (
            .O(fifo_rst_{fifo_site})
            );

        (* KEEP, DONT_TOUCH, LOC = "{fifo_site}" *)
        FIFO18E1 #(
            .ALMOST_EMPTY_OFFSET(5),
            .ALMOST_FULL_OFFSET(5)
            ) fifo_{fifo_site} (
                .RST(fifo_rst_{fifo_site})
            );

        (* KEEP, DONT_TOUCH, LOC = "{ramb_site}" *)
        RAMB18E1 #(
            ) bram_{ramb_site} (
            );
        '''.format(
            fifo_site=sites['FIFO18E1'],
            ramb_site=sites['RAMB18E1'],
        ))

    return params


def fifo36(tile_name, luts, lines, sites):
    """ FIFO36E1 consuming entire tile. """

    params = {}
    params['tile'] = tile_name
    params['Y0_IN_USE'] = True
    params['Y1_IN_USE'] = True
    params['FIFO_Y0_IN_USE'] = True
    params['FIFO_Y1_IN_USE'] = True

    data_width = random.choice((4, 9))
    if data_width == 4:
        ALMOST_EMPTY_OFFSET = 8184
        ALMOST_FULL_OFFSET = 8184
    else:
        ALMOST_EMPTY_OFFSET = 4087
        ALMOST_FULL_OFFSET = 4087

    lines.append(
        '''
        wire fifo_rst_{site};
        (* KEEP, DONT_TOUCH *)
        LUT6 fifo_lut_{site} (
            .O(fifo_rst_{site})
            );

        (* KEEP, DONT_TOUCH, LOC = "{site}" *)
        FIFO36E1 #(
            .ALMOST_EMPTY_OFFSET({ALMOST_EMPTY_OFFSET}),
            .ALMOST_FULL_OFFSET({ALMOST_FULL_OFFSET}),
            .DATA_WIDTH({data_width}),
            .INIT(36'hFF_FFFF_FFFF),
            .SRVAL(36'hFF_FFFF_FFFF)
            ) fifo_{site} (
                .RST(fifo_rst_{site})
            );
        '''.format(
            site=sites['RAMBFIFO36E1'],
            data_width=data_width,
            ALMOST_EMPTY_OFFSET=ALMOST_EMPTY_OFFSET,
            ALMOST_FULL_OFFSET=ALMOST_FULL_OFFSET))

    return params


def main():
    print('''
module top();
    ''')

    luts = LutMaker()
    lines = []

    params_list = []
    for tile_name, sites in gen_sites():
        gen_fun = random.choice(
            (ramb18, ramb18_2x, ramb36, fifo18, fifo18_ramb18, fifo36))
        params_list.append(gen_fun(tile_name, luts, lines, sites))

    for lut in luts.create_wires_and_luts():
        print(lut)

    for l in lines:
        print(l)

    print("endmodule")

    with open('params.json', 'w') as f:
        json.dump(params_list, f, indent=2)


if __name__ == '__main__':
    main()
