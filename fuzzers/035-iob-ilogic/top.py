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


def use_iserdese2(p, luts, connects):
    iobdelay = random.choice((
        'NONE',
        'BOTH',
        'IBUF',
        'IFD',
    ))

    p['IOBDELAY'] = verilog.quote(iobdelay)
    p['INIT_Q1'] = random.randint(0, 1)
    p['INIT_Q2'] = random.randint(0, 1)
    p['INIT_Q3'] = random.randint(0, 1)
    p['INIT_Q4'] = random.randint(0, 1)

    p['SRVAL_Q1'] = random.randint(0, 1)
    p['SRVAL_Q2'] = random.randint(0, 1)
    p['SRVAL_Q3'] = random.randint(0, 1)
    p['SRVAL_Q4'] = random.randint(0, 1)
    p['NUM_CE'] = random.randint(1, 2)

    p['IS_CLK_INVERTED'] = random.randint(0, 1)
    p['IS_CLKB_INVERTED'] = random.randint(0, 1)
    p['IS_OCLK_INVERTED'] = random.randint(0, 1)
    p['IS_OCLKB_INVERTED'] = random.randint(0, 1)
    p['IS_CLKDIV_INVERTED'] = random.randint(0, 1)
    p['IS_D_INVERTED'] = random.randint(0, 1)
    p['INTERFACE_TYPE'] = verilog.quote(
        random.choice(
            (
                'MEMORY',
                'MEMORY_DDR3',
                'MEMORY_QDR',
                'NETWORKING',
                'OVERSAMPLE',
            )))
    p['DATA_RATE'] = verilog.quote(random.choice((
        'SDR',
        'DDR',
    )))
    if verilog.unquote(p['DATA_RATE']) == 'SDR':
        data_widths = [2, 3, 4, 5, 6, 7, 8]
    else:
        data_widths = [4, 6, 8]

    p['DATA_WIDTH'] = random.choice(data_widths)
    p['SERDES_MODE'] = verilog.quote(random.choice(('MASTER', 'SLAVE')))

    use_delay = iobdelay != 'NONE'

    if iobdelay == 'NONE':
        p['mux_config'] = 'direct'
        p['iddr_mux_config'] = 'direct'
    elif iobdelay == 'BOTH':
        p['mux_config'] = 'idelay'
        p['iddr_mux_config'] = 'idelay'
    elif iobdelay == 'IBUF':
        p['mux_config'] = 'idelay'
        p['iddr_mux_config'] = 'direct'
    elif iobdelay == 'IFD':
        p['mux_config'] = 'direct'
        p['iddr_mux_config'] = 'idelay'

    p['OFB_USED'] = verilog.quote(random.choice(('TRUE', 'FALSE')))
    p['DYN_CLKDIV_INV_EN'] = verilog.quote(random.choice(('TRUE', 'FALSE')))
    p['DYN_CLK_INV_EN'] = verilog.quote(random.choice(('TRUE', 'FALSE')))

    if use_delay:
        print(
            """
    wire idelay_{site};

    (* KEEP, DONT_TOUCH, LOC = "{idelay_loc}" *)
    IDELAYE2 #(
    ) idelay_site_{site} (
        .IDATAIN({iwire}),
        .DATAOUT(idelay_{site})
        );""".format(**p),
            file=connects)

        p['ddly_connection'] = '.DDLY(idelay_{site}),'.format(**p)
    else:
        p['ddly_connection'] = ''

    if verilog.unquote(p['OFB_USED']) == 'TRUE':
        p['ODATA_RATE'] = verilog.quote(random.choice((
            'SDR',
            'DDR',
        )))
        if verilog.unquote(p['ODATA_RATE']) == 'SDR':
            data_widths = [2, 3, 4, 5, 6, 7, 8]
        else:
            data_widths = [4, 6, 8]

        p['ODATA_WIDTH'] = random.choice(data_widths)
        p['OSERDES_MODE'] = verilog.quote(random.choice(('MASTER', 'SLAVE')))

        if p['ODATA_WIDTH'] == 4 and verilog.unquote(p['ODATA_RATE']) == 'DDR':
            p['TRISTATE_WIDTH'] = 4
        else:
            p['TRISTATE_WIDTH'] = 1

        print(
            """
    wire tfb_{site};
    wire ofb_{site};

    (* KEEP, DONT_TOUCH, LOC = "{ologic_loc}" *)
    OSERDESE2 #(
        .SERDES_MODE({OSERDES_MODE}),
        .DATA_RATE_TQ({ODATA_RATE}),
        .DATA_RATE_OQ({ODATA_RATE}),
        .DATA_WIDTH({ODATA_WIDTH}),
        .TRISTATE_WIDTH({TRISTATE_WIDTH})
    ) oserdese2_{site} (
        .CLK(0),
        .CLKDIV(0),
        .D1(0),
        .TFB(tfb_{site}),
        .OQ({owire}),
        .TQ({twire}),
        .OFB(ofb_{site})
        );""".format(**p),
            file=connects)

        p['ofb_connections'] = """
        .OFB(ofb_{site}),
        """.format(**p)
    else:
        p['ofb_connections'] = ''

    if random.randint(0, 1):
        clknet = luts.get_next_output_net()
    else:
        clknet = random.choice((
            'clk_BUFG1',
            'clk_BUFG2',
        ))

    if random.randint(0, 1):
        clkbnet = luts.get_next_output_net()
    else:
        clkbnet = random.choice((
            'clk_BUFG1',
            'clk_BUFG2',
        ))

    if random.randint(0, 1):
        oclknet = luts.get_next_output_net()
    else:
        oclknet = random.choice((
            'clk_BUFG1',
            'clk_BUFG2',
        ))

    clkdiv = random.choice(('clk_BUFG3', 'clk_BUFG4'))

    p['DISABLE_CLOCKS'] = random.randint(0, 1)
    if p['DISABLE_CLOCKS']:
        clknet = '0'
        clkbnet = '0'
        oclknet = '0'
        clkdiv = '0'

    print(
        '''
    (* KEEP, DONT_TOUCH, LOC = "{ilogic_loc}" *)
    ISERDESE2 #(
        .SERDES_MODE({SERDES_MODE}),
        .INIT_Q1({INIT_Q1}),
        .INIT_Q2({INIT_Q2}),
        .INIT_Q3({INIT_Q3}),
        .INIT_Q4({INIT_Q4}),
        .SRVAL_Q1({SRVAL_Q1}),
        .SRVAL_Q2({SRVAL_Q2}),
        .SRVAL_Q3({SRVAL_Q3}),
        .SRVAL_Q4({SRVAL_Q4}),
        .DYN_CLKDIV_INV_EN({DYN_CLKDIV_INV_EN}),
        .DYN_CLK_INV_EN({DYN_CLK_INV_EN}),
        .INTERFACE_TYPE({INTERFACE_TYPE}),
        .IS_CLK_INVERTED({IS_CLK_INVERTED}),
        .IS_CLKB_INVERTED({IS_CLKB_INVERTED}),
        .IS_OCLK_INVERTED({IS_OCLK_INVERTED}),
        .IS_OCLKB_INVERTED({IS_OCLKB_INVERTED}),
        .IS_CLKDIV_INVERTED({IS_CLKDIV_INVERTED}),
        .IS_D_INVERTED({IS_D_INVERTED}),
        .OFB_USED({OFB_USED}),
        .NUM_CE({NUM_CE}),
        .DATA_RATE({DATA_RATE}),
        .DATA_WIDTH({DATA_WIDTH}),
        .IOBDELAY({IOBDELAY})
    ) iserdese2_{site} (
        {ddly_connection}
        {ofb_connections}
        .D({iwire}),
        .CLK({clknet}),
        .CLKB({clkbnet}),
        .OCLK({oclknet}),
        .O({onet}),
        .Q1({q1net}),
        .CLKDIV({clkdiv})
    );'''.format(
            clkdiv=clkdiv,
            clknet=clknet,
            clkbnet=clkbnet,
            oclknet=oclknet,
            onet=luts.get_next_input_net(),
            q1net=luts.get_next_input_net(),
            shiftout1net=luts.get_next_input_net(),
            shiftout2net=luts.get_next_input_net(),
            **p),
        file=connects)


def use_direct_and_iddr(p, luts, connects):
    p['mux_config'] = random.choice((
        'direct',
        'idelay',
        'none',
    ))

    p['iddr_mux_config'] = random.choice((
        'direct',
        'idelay',
        'none',
    ))

    if p['iddr_mux_config'] != 'none':
        p['INIT_Q1'] = random.randint(0, 1)
        p['INIT_Q2'] = random.randint(0, 1)
        p['IS_C_INVERTED'] = random.randint(0, 1)
        p['IS_D_INVERTED'] = random.randint(0, 1)
        p['SRTYPE'] = verilog.quote(random.choice(('SYNC', 'ASYNC')))
        p['DDR_CLK_EDGE'] = verilog.quote(
            random.choice(
                (
                    'OPPOSITE_EDGE',
                    'SAME_EDGE',
                    'SAME_EDGE_PIPELINED',
                )))

        print(
            '''
    (* KEEP, DONT_TOUCH, LOC = "{ilogic_loc}" *)
    IDDR #(
        .IS_D_INVERTED({IS_D_INVERTED}),
        .IS_C_INVERTED({IS_C_INVERTED}),
        .INIT_Q1({INIT_Q1}),
        .INIT_Q2({INIT_Q2}),
        .SRTYPE({SRTYPE}),
        .DDR_CLK_EDGE({DDR_CLK_EDGE})
    ) iddr_{site} (
        .C({cnet}),
        .D(iddr_d_{site}),
        .Q1({q1}),
        .Q2({q2})
        );
        '''.format(
                cnet=luts.get_next_output_net(),
                q1=luts.get_next_input_net(),
                q2=luts.get_next_input_net(),
                **p),
            file=connects)

    if p['iddr_mux_config'] == 'idelay' or p['mux_config'] == 'idelay' or p[
            'iddr_mux_config'] == 'tristate_feedback':
        print(
            """
    wire idelay_{site};

    (* KEEP, DONT_TOUCH, LOC = "{idelay_loc}" *)
    IDELAYE2 #(
    ) idelay_site_{site} (
        .IDATAIN({iwire}),
        .DATAOUT(idelay_{site})
        );""".format(**p),
            file=connects)

    print(
        """
    assign {owire} = {onet};
    assign {twire} = {tnet};
        """.format(
            onet=luts.get_next_output_net(),
            tnet=luts.get_next_output_net(),
            **p),
        file=connects)

    if p['iddr_mux_config'] == 'direct':
        print(
            '''
    assign iddr_d_{site} = {iwire};'''.format(**p, ),
            file=connects)
    elif p['iddr_mux_config'] == 'idelay':
        print(
            '''
    assign iddr_d_{site} = idelay_{site};'''.format(**p, ),
            file=connects)
    elif p['iddr_mux_config'] == 'tristate_feedback':
        print(
            '''
    assign iddr_d_{site} = tfb_{site} ? ofb_{site} : idelay_{site};'''.format(
                **p, ),
            file=connects)
    elif p['iddr_mux_config'] == 'none':
        pass
    else:
        assert False, p['mux_config']

    if p['mux_config'] == 'direct':
        print(
            '''
    assign {net} = {iwire};'''.format(
                net=luts.get_next_input_net(),
                **p,
            ),
            file=connects)
    elif p['mux_config'] == 'idelay':
        print(
            '''
    assign {net} = idelay_{site};'''.format(
                net=luts.get_next_input_net(),
                **p,
            ),
            file=connects)
    elif p['mux_config'] == 'none':
        pass
    else:
        assert False, p['mux_config']


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
    for idx, (tile, site) in enumerate(gen_sites()):
        if idx == 0:
            continue

        p = {}
        p['tile'] = tile
        p['site'] = site
        p['ilogic_loc'] = site.replace('IOB', 'ILOGIC')
        p['ologic_loc'] = site.replace('IOB', 'OLOGIC')
        p['idelay_loc'] = site.replace('IOB', 'IDELAY')
        p['IOSTANDARD'] = verilog.quote(iostandard)
        p['PULLTYPE'] = verilog.quote(random.choice(pulls))
        p['DRIVE'] = random.choice(drives)
        p['SLEW'] = verilog.quote(random.choice(slews))

        p['pad_wire'] = 'dio[{}]'.format(idx - 1)
        p['owire'] = 'do_buf[{}]'.format(idx - 1)
        p['iwire'] = 'di_buf[{}]'.format(idx - 1)
        p['twire'] = 't[{}]'.format(idx - 1)

        params.append(p)
        tile_params.append(
            (
                tile, site, p['pad_wire'], iostandard, p['DRIVE'],
                verilog.unquote(p['SLEW']) if p['SLEW'] else None,
                verilog.unquote(p['PULLTYPE'])))

    write_params(tile_params)

    print(
        '''
`define N_DI {n_di}

module top(input clk, inout wire [`N_DI-1:0] dio);
    wire [`N_DI-1:0] di_buf;
    wire [`N_DI-1:0] do_buf;
    wire [`N_DI-1:0] t;

    wire clk_BUFG1;
    wire clk_BUFG2;
    wire clk_BUFG3;
    wire clk_BUFG4;

    (* KEEP, DONT_TOUCH  *)
    BUFG bufg1(
        .O(clk_BUFG1)
        );
    (* KEEP, DONT_TOUCH  *)
    BUFG bufg2(
        .O(clk_BUFG2)
        );
    (* KEEP, DONT_TOUCH  *)
    BUFG bufg3(
        .O(clk_BUFG3)
        );
    (* KEEP, DONT_TOUCH  *)
    BUFG bufg4(
        .O(clk_BUFG4)
        );
    '''.format(n_di=idx))

    # Always output a LUT6 to make placer happy.
    print(
        '''
        (* KEEP, DONT_TOUCH *)
        LUT6 dummy_lut();
        ''')

    any_idelay = False

    for p in params:
        print(
            '''
        wire iddr_d_{site};

        (* KEEP, DONT_TOUCH, LOC = "{site}" *)
        IOBUF #(
            .IOSTANDARD({IOSTANDARD})
        ) ibuf_{site} (
            .IO({pad_wire}),
            .I({owire}),
            .O({iwire}),
            .T({twire})
            );
            '''.format(**p),
            file=connects)

        p['use_iserdese2'] = random.randint(0, 1)
        if p['use_iserdese2']:
            use_iserdese2(p, luts, connects)
        else:
            use_direct_and_iddr(p, luts, connects)

        if p['iddr_mux_config'] == 'idelay' or p['mux_config'] == 'idelay':
            any_idelay = True

    if any_idelay:
        print("""
    (* KEEP, DONT_TOUCH *)
    IDELAYCTRL();""")

    for l in luts.create_wires_and_luts():
        print(l)

    print(connects.getvalue())

    print("endmodule")

    with open('params.jl', 'w') as f:
        json.dump(params, f, indent=2)


if __name__ == '__main__':
    run()
