#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2022  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
import json
import io
import os
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import lut_maker
from prjxray import verilog
from prjxray.db import Database

from iostandards import *

def gen_sites():
    '''
    IOB18S: main IOB of a diff pair
    IOB18M: secondary IOB of a diff pair
    IOB18: not a diff pair. Relatively rare (at least in ROI...2 of them?)
    Focus on IOB18S to start
    '''
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        sites = {}
        for site_name, site_type in gridinfo.sites.items():
            if site_type in ['IOB18S', 'IOB18M']:
                sites[site_type] = site_name

        if sites:
            yield tile_name, sites


def write_params(params):
    pinstr = 'tile,site,pin,iostandard,drive,slew,pulltype\n'
    for vals in params:
        pinstr += ','.join(map(str, vals)) + '\n'

    open('params.csv', 'w').write(pinstr)


def run():
    tile_types = ['IBUF', 'OBUF', 'IOBUF_DCIEN', None, None]

    i_idx = 0
    o_idx = 0
    io_idx = 0

    iostandards = LVCMOS + SSTL + LVDS

    diff_map = {
        "SSTL15":  DIFF_SSTL15,
        "SSTL135": DIFF_SSTL135,
        "SSTL12":  DIFF_SSTL12,
    }

    vref_map = {
        "SSTL12":        .600,
        "SSTL135":       .675,
        "SSTL15":        .75,
        "DIFF_SSTL12":   .600,
        "DIFF_SSTL135":  .675,
        "DIFF_SSTL15":   .75,
    }

    only_diff_map = {
        "LVDS": ["LVDS"],
    }

    slews = ['FAST', 'SLOW']
    pulls = ["NONE", "KEEPER", "PULLDOWN", "PULLUP"]

    luts = lut_maker.LutMaker()

    connects = io.StringIO()

    tile_params = []
    params = {
        "tiles": [],
        'INTERNAL_VREF': {},
    }

    with open(os.path.join(os.getenv('FUZDIR'), 'build', 'iobanks.txt')) as f:
        iobanks = set()
        iob_sites = dict()
        for l in f:
            fields = l.split(',')
            iob_site = fields[0]
            iobank = fields[1].rstrip()

            iobanks.add(iobank)
            iob_sites[iob_site] = iobank

    params['iobanks'] = iobanks

    iostandard_map = dict()
    for iobank in iobanks:
        iostandard = random.choice(iostandards)
        if iostandard in SSTL:
            params['INTERNAL_VREF'][iobank] = vref_map[iostandard]

        iostandard_map[iobank] = iostandard

    params['iobanks'] = list(iobanks)

    any_idelay = False
    for tile, sites in gen_sites():
        iostandard = None

        site_bels = {}
        for site_type, site_name in sites.items():
            iobank = iob_sites[site_name]
            iostandard = iostandard_map[iobank]

            if iostandard in ['LVCMOS12']:
                drives = [2, 4, 6, 8]
            elif iostandard in ['LVCMOS15', 'LVCMOS18']:
                drives = [2, 4, 6, 8, 12, 16]
            elif iostandard in LVDS + SSTL:
                drives = None
            else:
                assert False, f"Unhandled iostandard: {iostandard}"

            if site_type.endswith('M'):
                if iostandard in diff_map:
                    site_bels[site_type] = random.choice(
                        tile_types + ['IBUFDS', 'OBUFDS', 'OBUFTDS'])
                elif iostandard in only_diff_map:
                    site_bels[site_type] = random.choice(
                        ['IBUFDS', 'OBUFDS', 'OBUFTDS', None, None])
                else:
                    site_bels[site_type] = random.choice(tile_types)
                is_m_diff = site_bels[site_type] is not None and site_bels[
                    site_type].endswith('DS')
            else:
                site_bels[site_type] = random.choice(tile_types)

        if is_m_diff or iostandard in only_diff_map:
            site_bels['IOB18S'] = None

        for site_type, site in sites.items():
            p = {}
            p['tile'] = tile
            p['site'] = site
            p['type'] = site_bels[site_type]

            if p['type'] is not None and p['type'].endswith('DS'):
                if iostandard in diff_map:
                    iostandard_site = random.choice(diff_map[iostandard])
                elif iostandard in only_diff_map:
                    iostandard_site = random.choice(only_diff_map[iostandard])
                p['pair_site'] = sites['IOB18S']
            else:
                iostandard_site = iostandard

            p['IOSTANDARD'] = verilog.quote(iostandard_site)
            p['PULLTYPE'] = verilog.quote(random.choice(pulls))

            if p['type'] is None:
                p['pad_wire'] = None
            elif p['type'] == 'IBUF':
                p['pad_wire'] = 'di[{}]'.format(i_idx)
                p['IDELAY_ONLY'] = random.randint(0, 1)
                if not p['IDELAY_ONLY']:
                    p['owire'] = luts.get_next_input_net()
                else:
                    any_idelay = True
                    p['owire'] = 'idelay_{site}'.format(**p)

                p['DRIVE'] = None
                p['SLEW'] = None
                p['IBUF_LOW_PWR'] = random.randint(0, 1)
                i_idx += 1
            elif p['type'] == 'IBUFDS':
                p['pad_wire'] = 'di[{}]'.format(i_idx)
                i_idx += 1
                p['bpad_wire'] = 'di[{}]'.format(i_idx)
                i_idx += 1

                p['IDELAY_ONLY'] = random.randint(0, 1)
                p['DIFF_TERM'] = random.randint(0, 1) if iostandard in LVDS else 0
                if not p['IDELAY_ONLY']:
                    p['owire'] = luts.get_next_input_net()
                else:
                    any_idelay = True
                    p['owire'] = 'idelay_{site}'.format(**p)

                p['DRIVE'] = None
                p['SLEW'] = None
                p['IBUF_LOW_PWR'] = random.randint(0, 1)

            elif p['type'] == 'OBUF':
                p['pad_wire'] = 'do[{}]'.format(o_idx)
                p['iwire'] = luts.get_next_output_net()
                if drives is not None:
                    p['DRIVE'] = random.choice(drives)
                else:
                    p['DRIVE'] = None
                p['SLEW'] = verilog.quote(random.choice(slews))

                o_idx += 1
            elif p['type'] == 'OBUFDS':
                p['pad_wire'] = 'do[{}]'.format(o_idx)
                o_idx += 1
                p['bpad_wire'] = 'do[{}]'.format(o_idx)
                o_idx += 1
                p['iwire'] = luts.get_next_output_net()
                if drives is not None:
                    p['DRIVE'] = random.choice(drives)
                else:
                    p['DRIVE'] = None
                p['SLEW'] = verilog.quote(random.choice(slews))
            elif p['type'] == 'OBUFTDS':
                p['pad_wire'] = 'do[{}]'.format(o_idx)
                o_idx += 1
                p['bpad_wire'] = 'do[{}]'.format(o_idx)
                o_idx += 1
                p['tristate_wire'] = random.choice(
                    ('0', luts.get_next_output_net()))
                p['iwire'] = luts.get_next_output_net()
                if drives is not None:
                    p['DRIVE'] = random.choice(drives)
                else:
                    p['DRIVE'] = None
                p['SLEW'] = verilog.quote(random.choice(slews))
            elif p['type'] == 'IOBUF_DCIEN':
                p['pad_wire'] = 'dio[{}]'.format(io_idx)
                p['iwire'] = luts.get_next_output_net()
                p['owire'] = luts.get_next_input_net()
                if drives is not None:
                    p['DRIVE'] = random.choice(drives)
                else:
                    p['DRIVE'] = None
                p['SLEW'] = verilog.quote(random.choice(slews))
                p['tristate_wire'] = random.choice(
                    ('0', luts.get_next_output_net()))
                p['ibufdisable_wire'] = random.choice(
                    ('0', luts.get_next_output_net()))
                p['dcitermdisable_wire'] = random.choice(
                    ('0', luts.get_next_output_net()))
                io_idx += 1

            if 'DRIVE' in p:
                if p['DRIVE'] is not None:
                    p['DRIVE_STR'] = '.DRIVE({}),'.format(p['DRIVE'])
                else:
                    p['DRIVE_STR'] = ''

            if 'SLEW' in p:
                p['SLEW_STR'] = ''
                if iostandard in only_diff_map:
                    p['SLEW'] = None
                elif p['DRIVE'] is not None:
                    p['SLEW_STR'] = '.SLEW({}),'.format(p['SLEW'])

            if p['type'] is not None:
                tile_params.append(
                    (
                        tile,
                        site,
                        p['pad_wire'],
                        iostandard_site,
                        p['DRIVE'],
                        verilog.unquote(p['SLEW']) if p['SLEW'] else None,
                        verilog.unquote(p['PULLTYPE']),
                    ))
            params['tiles'].append(p)

    write_params(tile_params)

    with open('iobank_vref.csv', 'w') as f:
        for iobank, vref in params['INTERNAL_VREF'].items():
            f.write('{},{}\n'.format(iobank, vref))

    print(
        '''
`define N_DI {n_di}
`define N_DO {n_do}
`define N_DIO {n_dio}

module top(input wire [`N_DI-1:0] di, output wire [`N_DO-1:0] do, inout wire [`N_DIO-1:0] dio, input refclk);
    '''.format(n_di=i_idx, n_do=o_idx, n_dio=io_idx))

    if any_idelay:
        print('''
        (* KEEP, DONT_TOUCH *)
        IDELAYCTRL(.REFCLK(refclk));''')

    # Always output a LUT6 to make placer happy.
    print('''
        (* KEEP, DONT_TOUCH *)
        LUT6 dummy_lut();''')

    for p in params['tiles']:
        if p['type'] is None:
            continue
        elif p['type'] == 'IBUF':
            print(
                '''
        wire idelay_{site};

        (* KEEP, DONT_TOUCH *)
        IBUF #(
            .IBUF_LOW_PWR({IBUF_LOW_PWR}),
            .IOSTANDARD({IOSTANDARD})
        ) ibuf_{site} (
            .I({pad_wire}),
            .O({owire})
            );'''.format(**p),
                file=connects)
            if p['IDELAY_ONLY']:
                print(
                    """
        (* KEEP, DONT_TOUCH *)
        IDELAYE2 idelay_site_{site} (
            .IDATAIN(idelay_{site})
            );""".format(**p),
                    file=connects)

        elif p['type'] == 'IBUFDS':
            print(
                '''
        wire idelay_{site};

        (* KEEP, DONT_TOUCH *)
        IBUFDS #(
            .IBUF_LOW_PWR({IBUF_LOW_PWR}),
            .DIFF_TERM({DIFF_TERM}),
            .IOSTANDARD({IOSTANDARD})
        ) ibuf_{site} (
            .I({pad_wire}),
            .IB({bpad_wire}),
            .O({owire})
            );'''.format(**p),
                file=connects)
            if p['IDELAY_ONLY']:
                print(
                    """
        (* KEEP, DONT_TOUCH *)
        IDELAYE2 idelay_site_{site} (
            .IDATAIN(idelay_{site})
            );""".format(**p),
                    file=connects)

        elif p['type'] == 'OBUF':
            print(
                '''
        (* KEEP, DONT_TOUCH *)
        OBUF #(
            {DRIVE_STR}
            {SLEW_STR}
            .IOSTANDARD({IOSTANDARD})
        ) obuf_{site} (
            .O({pad_wire}),
            .I({iwire})
            );'''.format(**p),
                file=connects)
        elif p['type'] == 'OBUFDS':
            print(
                '''
        (* KEEP, DONT_TOUCH *)
        OBUFDS #(
            {DRIVE_STR}
            {SLEW_STR}
            .IOSTANDARD({IOSTANDARD})
        ) obufds_{site} (
            .O({pad_wire}),
            .OB({bpad_wire}),
            .I({iwire})
            );'''.format(**p),
                file=connects)
        elif p['type'] == 'OBUFTDS':
            print(
                '''
        (* KEEP, DONT_TOUCH *)
        OBUFTDS #(
            {DRIVE_STR}
            {SLEW_STR}
            .IOSTANDARD({IOSTANDARD})
        ) obufds_{site} (
            .O({pad_wire}),
            .OB({bpad_wire}),
            .T({tristate_wire}),
            .I({iwire})
            );'''.format(**p),
                file=connects)
        elif p['type'] == 'IOBUF_DCIEN':
            print(
                '''
        (* KEEP, DONT_TOUCH *)
        IOBUF_DCIEN #(
            {DRIVE_STR}
            {SLEW_STR}
            .IOSTANDARD({IOSTANDARD})
        ) ibuf_{site} (
            .IO({pad_wire}),
            .I({iwire}),
            .O({owire}),
            .T({tristate_wire}),
            .IBUFDISABLE({ibufdisable_wire}),
            .DCITERMDISABLE({dcitermdisable_wire})
            );'''.format(**p),
                file=connects)

    for l in luts.create_wires_and_luts():
        print(l)

    print(connects.getvalue())

    print("endmodule")

    with open('params.json', 'w') as f:
        json.dump(params, f, indent=2)


if __name__ == '__main__':
    run()
