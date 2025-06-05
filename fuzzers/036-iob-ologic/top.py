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
import io
import os
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import lut_maker
from prjxray import verilog
from prjxray.db import Database


def gen_sites():
    '''
    IOB33S: main IOB of a diff pair
    IOB33M: secondary IOB of a diff pair
    IOB33: not a diff pair. Relatively rare (at least in ROI...2 of them?)
    Focus on IOB33S to start
    '''
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site_name, site_type in gridinfo.sites.items():
            if site_type in ['IOB33S', 'IOB33M']:
                yield tile_name, site_name


def write_params(params):
    pinstr = 'tile,site,pin,iostandard,drive,slew\n'
    for vals in params:
        pinstr += ','.join(map(str, vals)) + '\n'

    open('params.csv', 'w').write(pinstr)


def use_oserdese2(p, luts, connects):

    p['oddr_mux_config'] = 'none'
    p['tddr_mux_config'] = 'none'

    p['DATA_RATE_OQ'] = verilog.quote(random.choice((
        'SDR',
        'DDR',
    )))

    p['DATA_RATE_TQ'] = verilog.quote(random.choice((
        'BUF',
        'SDR',
        'DDR',
    )))

    if verilog.unquote(p['DATA_RATE_OQ']) == 'SDR':
        data_widths = [2, 3, 4, 5, 6, 7, 8]
    else:
        data_widths = [4, 6, 8, 10, 14]

    p['DATA_WIDTH'] = random.choice(data_widths)

    if p['DATA_WIDTH'] == 4 and verilog.unquote(
            p['DATA_RATE_OQ']) == 'DDR' and verilog.unquote(
                p['DATA_RATE_TQ']) == 'DDR':
        tristate_width = 4
    else:
        tristate_width = 1
    p['SERDES_MODE'] = verilog.quote(random.choice(('MASTER', 'SLAVE')))

    p['TRISTATE_WIDTH'] = tristate_width
    p['OSERDES_MODE'] = verilog.quote(random.choice(('MASTER', 'SLAVE')))

    if p['io']:
        p['TFB'] = '.TFB(tfb_{site}),'.format(**p)
        p['TQ'] = '.TQ({twire}),'.format(**p)
        p['t1net'] = luts.get_next_output_net()
        p['t2net'] = luts.get_next_output_net()
        p['t3net'] = luts.get_next_output_net()
        p['t4net'] = luts.get_next_output_net()
        p['tcenet'] = luts.get_next_output_net()

        for idx in range(4):
            p['IS_T{}_INVERTED'.format(idx + 1)] = random.randint(0, 1)
    else:
        p['TFB'] = '.TFB(),'
        p['TQ'] = '.TQ(),'
        p['t1net'] = ''
        p['t2net'] = ''
        p['t3net'] = ''
        p['t4net'] = ''
        p['tcenet'] = ''

        for idx in range(4):
            p['IS_T{}_INVERTED'.format(idx + 1)] = 0

    p['SRVAL_OQ'] = random.randint(0, 1)
    p['SRVAL_TQ'] = random.randint(0, 1)
    p['INIT_OQ'] = random.randint(0, 1)
    p['INIT_TQ'] = random.randint(0, 1)

    for idx in range(8):
        p['IS_D{}_INVERTED'.format(idx + 1)] = random.randint(0, 1)

    p['IS_CLK_INVERTED'] = random.randint(0, 1)
    p['IS_CLKDIV_INVERTED'] = random.randint(0, 1)

    clk_connections = ''
    p['CLK_USED'] = random.randint(0, 1)
    p['CLKDIV_USED'] = random.randint(0, 1)
    if p['CLK_USED']:
        clk_connections += '''
        .CLK({}),'''.format(luts.get_next_output_net())
    if p['CLKDIV_USED']:
        clk_connections += '''
        .CLKDIV({}),'''.format(luts.get_next_output_net())

    print(
        '''
    (* KEEP, DONT_TOUCH, LOC = "{ologic_loc}" *)
    OSERDESE2 #(
        .SERDES_MODE({OSERDES_MODE}),
        .DATA_RATE_TQ({DATA_RATE_TQ}),
        .DATA_RATE_OQ({DATA_RATE_OQ}),
        .DATA_WIDTH({DATA_WIDTH}),
        .TRISTATE_WIDTH({TRISTATE_WIDTH}),
        .SRVAL_OQ({SRVAL_OQ}),
        .SRVAL_TQ({SRVAL_TQ}),
        .INIT_OQ({INIT_OQ}),
        .INIT_TQ({INIT_TQ}),
        .IS_T1_INVERTED({IS_T1_INVERTED}),
        .IS_T2_INVERTED({IS_T2_INVERTED}),
        .IS_T3_INVERTED({IS_T3_INVERTED}),
        .IS_T4_INVERTED({IS_T4_INVERTED}),
        .IS_D1_INVERTED({IS_D1_INVERTED}),
        .IS_D2_INVERTED({IS_D2_INVERTED}),
        .IS_D3_INVERTED({IS_D3_INVERTED}),
        .IS_D4_INVERTED({IS_D4_INVERTED}),
        .IS_D5_INVERTED({IS_D5_INVERTED}),
        .IS_D6_INVERTED({IS_D6_INVERTED}),
        .IS_D7_INVERTED({IS_D7_INVERTED}),
        .IS_D8_INVERTED({IS_D8_INVERTED}),
        .IS_CLK_INVERTED({IS_CLK_INVERTED}),
        .IS_CLKDIV_INVERTED({IS_CLKDIV_INVERTED})
    ) oserdese2_{site} (
        .OQ({owire}),
        {TFB}
        {TQ}
        {clk_connections}
        .D1({d1net}),
        .D2({d2net}),
        .D3({d3net}),
        .D4({d4net}),
        .D5({d5net}),
        .D6({d6net}),
        .D7({d7net}),
        .D8({d8net}),
        .OCE({ocenet}),
        .RST({rstnet}),
        .T1({t1net}),
        .T2({t2net}),
        .T3({t3net}),
        .T4({t4net}),
        .TCE({tcenet})
        );'''.format(
            clk_connections=clk_connections,
            rstnet=luts.get_next_output_net(),
            d1net=luts.get_next_output_net(),
            d2net=luts.get_next_output_net(),
            d3net=luts.get_next_output_net(),
            d4net=luts.get_next_output_net(),
            d5net=luts.get_next_output_net(),
            d6net=luts.get_next_output_net(),
            d7net=luts.get_next_output_net(),
            d8net=luts.get_next_output_net(),
            ocenet=luts.get_next_output_net(),
            ofb_wire=luts.get_next_input_net(),
            **p),
        file=connects)


def use_direct_and_oddr(p, luts, connects):
    p['oddr_mux_config'] = random.choice((
        'direct',
        'lut',
        'none',
    ))

    if p['io']:
        if p['oddr_mux_config'] != 'lut':
            p['tddr_mux_config'] = random.choice((
                'direct',
                'lut',
                'none',
            ))
        else:
            p['tddr_mux_config'] = random.choice((
                'lut',
                'none',
            ))
    else:
        p['tddr_mux_config'] = 'none'

    # toddr and oddr share the same clk
    if random.randint(0, 1):
        clknet = luts.get_next_output_net()
        p['IS_CLK_INVERTED'] = 0
    else:
        clknet = 'bufg_o'
        p['IS_CLK_INVERTED'] = random.randint(0, 1)

    if p['tddr_mux_config'] == 'direct':
        p['TINIT'] = random.randint(0, 1)
        p['TSRTYPE'] = verilog.quote(random.choice(('SYNC', 'ASYNC')))
        p['TDDR_CLK_EDGE'] = verilog.quote('OPPOSITE_EDGE')

        # Note: it seems that CLK_EDGE setting is ignored for TDDR
        p['TDDR_CLK_EDGE'] = verilog.quote(
            random.choice(('OPPOSITE_EDGE', 'SAME_EDGE')))

        p['t_sr_used'] = random.choice(('None', 'S', 'R'))
        if p['t_sr_used'] == 'None':
            p['t_srnet'] = ''
        elif p['t_sr_used'] == 'S':
            p['srnet'] = luts.get_next_output_net()
            p['t_srnet'] = '.S({}),\n'.format(p['srnet'])
        elif p['t_sr_used'] == 'R':
            p['srnet'] = luts.get_next_output_net()
            p['t_srnet'] = '.R({}),\n'.format(p['srnet'])

        print(
            '''
    (* KEEP, DONT_TOUCH, LOC = "{ologic_loc}" *)
    ODDR #(
        .INIT({TINIT}),
        .SRTYPE({TSRTYPE}),
        .DDR_CLK_EDGE({TDDR_CLK_EDGE}),
        .IS_C_INVERTED({IS_CLK_INVERTED})
    ) toddr_{site} (
        .C({cnet}),
        .D1({d1net}),
        .D2({d2net}),
        .CE({cenet}),
        {t_srnet}
        .Q(tddr_d_{site})
        );
        '''.format(
                cnet=clknet,
                d1net=luts.get_next_output_net(),
                d2net=luts.get_next_output_net(),
                cenet=luts.get_next_output_net(),
                **p),
            file=connects)

    if p['tddr_mux_config'] == 'direct':
        print(
            '''
    assign {twire} = tddr_d_{site};'''.format(**p, ),
            file=connects)
    elif p['tddr_mux_config'] == 'lut':
        print(
            '''
    assign {twire} = {lut};'''.format(lut=luts.get_next_output_net(), **p),
            file=connects)
        pass
    elif p['tddr_mux_config'] == 'none':
        pass
    else:
        assert False, p['tddr_mux_config']

    if p['oddr_mux_config'] == 'direct':
        p['QINIT'] = random.randint(0, 1)
        p['SRTYPE'] = verilog.quote(random.choice(('SYNC', 'ASYNC')))
        p['ODDR_CLK_EDGE'] = verilog.quote(
            random.choice((
                'OPPOSITE_EDGE',
                'SAME_EDGE',
            )))

        p['o_sr_used'] = random.choice(('None', 'S', 'R'))
        if p['o_sr_used'] == 'None':
            p['o_srnet'] = ''
        elif p['o_sr_used'] == 'S':
            if 'srnet' not in p:
                p['srnet'] = luts.get_next_output_net()
            p['o_srnet'] = '.S({}),\n'.format(p['srnet'])
        elif p['o_sr_used'] == 'R':
            if 'srnet' not in p:
                p['srnet'] = luts.get_next_output_net()
            p['o_srnet'] = '.R({}),\n'.format(p['srnet'])

        print(
            '''
    (* KEEP, DONT_TOUCH, LOC = "{ologic_loc}" *)
    ODDR #(
        .INIT({QINIT}),
        .SRTYPE({SRTYPE}),
        .DDR_CLK_EDGE({ODDR_CLK_EDGE}),
        .IS_C_INVERTED({IS_CLK_INVERTED})
    ) oddr_{site} (
        .C({cnet}),
        .D1({d1net}),
        .D2({d2net}),
        .CE({cenet}),
        {o_srnet}
        .Q(oddr_d_{site})
        );
        '''.format(
                cnet=clknet,
                d1net=luts.get_next_output_net(),
                d2net=luts.get_next_output_net(),
                cenet=luts.get_next_output_net(),
                **p),
            file=connects)

    if p['oddr_mux_config'] == 'direct':
        print(
            '''
    assign {owire} = oddr_d_{site};'''.format(**p, ),
            file=connects)
    elif p['oddr_mux_config'] == 'lut':
        print(
            '''
    assign {owire} = {lut};'''.format(lut=luts.get_next_output_net(), **p),
            file=connects)
        pass
    elif p['oddr_mux_config'] == 'none':
        pass
    else:
        assert False, p['oddr_mux_config']


def run():
    iostandards = [
        'LVCMOS12', 'LVCMOS15', 'LVCMOS18', 'LVCMOS25', 'LVCMOS33', 'LVTTL'
    ]
    iostandard = random.choice(iostandards)

    if iostandard in ['LVTTL', 'LVCMOS18']:
        drives = [4, 8, 12, 16, 24]
    elif iostandard == 'LVCMOS12':
        drives = [4, 8, 12]
    else:
        drives = [4, 8, 12, 16]

    slews = ['FAST', 'SLOW']
    pulls = ["NONE", "KEEPER", "PULLDOWN", "PULLUP"]

    luts = lut_maker.LutMaker()

    connects = io.StringIO()

    tile_params = []
    params = []

    ndio = 0
    ndo = 0
    for idx, (tile, site) in enumerate(gen_sites()):
        if idx == 0:
            continue

        p = {}
        p['tile'] = tile
        p['site'] = site
        p['ilogic_loc'] = site.replace('IOB', 'ILOGIC')
        p['ologic_loc'] = site.replace('IOB', 'OLOGIC')
        p['IOSTANDARD'] = verilog.quote(iostandard)
        p['PULLTYPE'] = verilog.quote(random.choice(pulls))
        p['DRIVE'] = random.choice(drives)
        p['SLEW'] = verilog.quote(random.choice(slews))

        p['io'] = random.randint(0, 1)
        p['owire'] = 'do_buf[{}]'.format(idx - 1)

        if p['io']:
            p['pad_wire'] = 'dio[{}]'.format(ndio)
            ndio += 1

            p['iwire'] = 'di_buf[{}]'.format(idx - 1)
            p['twire'] = 't[{}]'.format(idx - 1)
        else:
            p['pad_wire'] = 'do[{}]'.format(ndo)
            ndo += 1

        params.append(p)
        tile_params.append(
            (
                tile, site, p['pad_wire'], iostandard, p['DRIVE'],
                verilog.unquote(p['SLEW']) if p['SLEW'] else None,
                verilog.unquote(p['PULLTYPE'])))

    write_params(tile_params)

    print(
        '''
`define N_DO {n_do}
`define N_DIO {n_dio}

module top(input clk, output wire [`N_DO-1:0] do, inout wire [`N_DIO-1:0] dio);
    wire [(`N_DIO+`N_DO)-1:0] di_buf;
    wire [(`N_DIO+`N_DO)-1:0] do_buf;
    wire [(`N_DIO+`N_DO)-1:0] t;
    '''.format(n_dio=ndio, n_do=ndo))

    # Always output a LUT6 to make placer happy.
    print(
        '''
        (* KEEP, DONT_TOUCH *)
        LUT6 dummy_lut();

        wire bufg_o;
        (* KEEP, DONT_TOUCH *)
        BUFG (.O(bufg_o));
        ''')

    for p in params:
        if p['io']:
            print(
                '''
        wire oddr_d_{site};

        (* KEEP, DONT_TOUCH, LOC = "{site}" *)
        IOBUF #(
            .IOSTANDARD({IOSTANDARD})
        ) obuf_{site} (
            .IO({pad_wire}),
            .I({owire}),
            .O({iwire}),
            .T({twire})
            );
            '''.format(**p),
                file=connects)
        else:
            print(
                '''
        wire oddr_d_{site};

        (* KEEP, DONT_TOUCH, LOC = "{site}" *)
        OBUF #(
            .IOSTANDARD({IOSTANDARD})
        ) obuf_{site} (
            .O({pad_wire}),
            .I({owire})
            );
            '''.format(**p),
                file=connects)

        p['use_oserdese2'] = random.randint(0, 1)
        if p['use_oserdese2']:
            use_oserdese2(p, luts, connects)
        else:
            use_direct_and_oddr(p, luts, connects)

    for l in luts.create_wires_and_luts():
        print(l)

    print(connects.getvalue())

    print("endmodule")

    with open('params.jl', 'w') as f:
        json.dump(params, f, indent=2)


if __name__ == '__main__':
    run()
