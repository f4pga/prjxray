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
import json
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import verilog
from prjxray.db import Database


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile)
        gridinfo = grid.gridinfo_at_loc(loc)
        if gridinfo.tile_type in ['DSP_L', 'DSP_R']:
            for site in sorted(gridinfo.sites.keys()):
                if gridinfo.sites[site] == 'DSP48E1':
                    yield tile, site


def fuzz(*args):
    if len(args) == 1 and isinstance(args[0], int):
        # Argument indicates that we should generate a random integer with
        # args[0] number of bits.
        return random.getrandbits(args[0])
    else:
        # Otherwise make a random choice
        return random.choice(*args)


def run():
    verilog.top_harness(48, 48)

    print('module roi(input clk, input [47:0] din, output [47:0] dout);')

    data = {}
    data['instances'] = []

    sites = list(gen_sites())

    for i, (tile, site) in enumerate(sites):
        synthesis = '(* KEEP, DONT_TOUCH, LOC = "%s" *)' % (site)
        module = 'DSP48E1'
        instance = 'INST_%s' % (site)
        ports = {}
        params = {}

        ports['A'] = '{30{1\'b1}}'
        ports['ACIN'] = '{30{1\'b1}}'
        ports['ACOUT'] = '30\'b0'
        ports['ALUMODE'] = 'din[3:0]'
        ports['B'] = '{18{1\'b1}}'
        ports['BCIN'] = '{18{1\'b1}}'
        ports['BCOUT'] = '18\'b0'
        ports['C'] = '{48{1\'b1}}'
        ports['CARRYCASCIN'] = '1\'b1'
        ports['CARRYCASCOUT'] = '1\'b0'
        ports['CARRYIN'] = 'din[4]'
        ports['CARRYINSEL'] = '3\'b000'
        ports['CARRYOUT'] = '4\'b0'
        ports['CEA1'] = '1\'b1'
        ports['CEA2'] = '1\'b1'
        ports['CEAD'] = '1\'b1'
        ports['CEALUMODE'] = '1\'b1'
        ports['CEB1'] = '1\'b1'
        ports['CEB2'] = '1\'b1'
        ports['CEC'] = '1\'b1'
        ports['CECARRYIN'] = '1\'b1'
        ports['CECTRL'] = '1\'b1'
        ports['CED'] = '1\'b1'
        ports['CEINMODE'] = '1\'b1'
        ports['CEM'] = '1\'b1'
        ports['CEP'] = '1\'b1'
        ports['CLK'] = 'clk'
        ports['D'] = '{25{1\'b1}}'
        ports['INMODE'] = 'din[9:5]'
        #ports['MULTISIGNIN'] = '1\'b1'
        #ports['MULTISIGNOUT'] = '1\'b0'
        ports['OPMODE'] = 'din[16:10]'
        ports['OVERFLOW'] = '1\'b0'
        ports['P'] = '48\'b0'
        ports['PATTERNBDETECT'] = '1\'b0'
        ports['PATTERNDETECT'] = '1\'b0'
        ports['PCIN'] = '{48{1\'b1}}'
        ports['PCOUT'] = '48\'b0'
        ports['RSTA'] = '1\'b1'
        ports['RSTALLCARRYIN'] = '1\'b1'
        ports['RSTALUMODE'] = '1\'b1'
        ports['RSTB'] = '1\'b1'
        ports['RSTC'] = '1\'b1'
        ports['RSTCTRL'] = '1\'b1'
        ports['RSTD'] = '1\'b1'
        ports['RSTINMODE'] = '1\'b1'
        ports['RSTM'] = '1\'b1'
        ports['RSTP'] = '1\'b1'
        ports['UNDERFLOW'] = '1\'b0'

        params['ADREG'] = fuzz((0, 1))
        params['ALUMODEREG'] = fuzz((0, 1))
        params['AREG'] = fuzz((0, 1, 2))
        if params['AREG'] == 0 or params['AREG'] == 1:
            params['ACASCREG'] = params['AREG']
        else:
            params['ACASCREG'] = fuzz((1, 2))
        params['BREG'] = fuzz((0, 1, 2))
        if params['BREG'] == 0 or params['BREG'] == 1:
            params['BCASCREG'] = params['BREG']
        else:
            params['BCASCREG'] = fuzz((1, 2))
        params['CARRYINREG'] = fuzz((0, 1))
        params['CARRYINSELREG'] = fuzz((0, 1))
        params['CREG'] = fuzz((0, 1))
        params['DREG'] = fuzz((0, 1))
        params['INMODEREG'] = fuzz((0, 1))
        params['OPMODEREG'] = fuzz((0, 1))
        params['PREG'] = fuzz((0, 1))
        params['A_INPUT'] = verilog.quote(fuzz(('DIRECT', 'CASCADE')))
        params['B_INPUT'] = verilog.quote(fuzz(('DIRECT', 'CASCADE')))
        params['USE_DPORT'] = verilog.quote(fuzz(('TRUE', 'FALSE')))
        params['USE_SIMD'] = verilog.quote(fuzz(('ONE48', 'TWO24', 'FOUR12')))
        params['USE_MULT'] = verilog.quote(
            'NONE' if params['USE_SIMD'] != verilog.quote('ONE48') else fuzz(
                ('NONE', 'MULTIPLY', 'DYNAMIC')))
        params['MREG'] = 0 if params['USE_MULT'] == verilog.quote(
            'NONE') else fuzz((0, 1))
        params['AUTORESET_PATDET'] = verilog.quote(
            fuzz(('NO_RESET', 'RESET_MATCH', 'RESET_NOT_MATCH')))
        params['MASK'] = '48\'d%s' % fuzz(48)
        params['PATTERN'] = '48\'d%s' % fuzz(48)
        params['SEL_MASK'] = verilog.quote(
            fuzz(('MASK', 'C', 'ROUNDING_MODE1', 'ROUNDING_MODE2')))
        params['USE_PATTERN_DETECT'] = verilog.quote(
            fuzz(('NO_PATDET', 'PATDET')))

        params['IS_ALUMODE_INVERTED'] = fuzz(4)
        params['IS_CARRYIN_INVERTED'] = fuzz((0, 1))
        params['IS_CLK_INVERTED'] = fuzz((0, 1))
        params['IS_INMODE_INVERTED'] = fuzz(5)
        params['IS_OPMODE_INVERTED'] = fuzz(7)

        verilog.instance(synthesis + ' ' + module, instance, ports, params)

        params['TILE'] = tile
        params['SITE'] = site

        data['instances'].append(params)

    with open('params.json', 'w') as fp:
        json.dump(data, fp)

    print("endmodule")


if __name__ == '__main__':
    run()
