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
    db = Database(util.get_db_root())
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
        data_widths = [4, 6, 8]

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

    print(
        '''
    (* KEEP, DONT_TOUCH, LOC = "{ologic_loc}" *)
    OSERDESE2 #(
        .SERDES_MODE({OSERDES_MODE}),
        .DATA_RATE_TQ({DATA_RATE_TQ}),
        .DATA_RATE_OQ({DATA_RATE_OQ}),
        .DATA_WIDTH({DATA_WIDTH}),
        .TRISTATE_WIDTH({TRISTATE_WIDTH})
    ) oserdese2_{site} (
        .OQ({owire}),
        .TFB(tfb_{site}),
        .TQ({twire}),
        .CLK({clknet}),
        .CLKDIV({clkdivnet}),
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
            clknet=luts.get_next_output_net(),
            clkdivnet=luts.get_next_output_net(),
            rstnet=luts.get_next_output_net(),
            d1net=luts.get_next_output_net(),
            d2net=luts.get_next_output_net(),
            d3net=luts.get_next_output_net(),
            d4net=luts.get_next_output_net(),
            d5net=luts.get_next_output_net(),
            d6net=luts.get_next_output_net(),
            d7net=luts.get_next_output_net(),
            d8net=luts.get_next_output_net(),
            t1net=luts.get_next_output_net(),
            t2net=luts.get_next_output_net(),
            t3net=luts.get_next_output_net(),
            t4net=luts.get_next_output_net(),
            tcenet=luts.get_next_output_net(),
            ocenet=luts.get_next_output_net(),
            ofb_wire=luts.get_next_input_net(),
            **p),
        file=connects)


def use_direct_and_oddr(p, luts, connects):
    p['oddr_mux_config'] = random.choice((
        'direct',
        'none',
    ))

    p['tddr_mux_config'] = random.choice((
        'direct',
        'none',
    ))

    # toddr and oddr share the same clk
    clknet = luts.get_next_output_net()

    if p['tddr_mux_config'] != 'none':
        p['TINIT'] = random.randint(0, 1)
        p['TSRTYPE'] = verilog.quote(random.choice(('SYNC', 'ASYNC')))
        p['TDDR_CLK_EDGE'] = verilog.quote('OPPOSITE_EDGE')

        # Note: it seems that CLK_EDGE setting is ignored for TDDR
        p['TDDR_CLK_EDGE'] = verilog.quote(
            random.choice(('OPPOSITE_EDGE', 'SAME_EDGE')))
        print(
            '''
    (* KEEP, DONT_TOUCH, LOC = "{ologic_loc}" *)
    ODDR #(
        .INIT({TINIT}),
        .SRTYPE({TSRTYPE}),
        .DDR_CLK_EDGE({TDDR_CLK_EDGE})
    ) toddr_{site} (
        .C({cnet}),
        .D1({d1net}),
        .D2({d2net}),
        .CE({cenet}),
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
    elif p['tddr_mux_config'] == 'none':
        pass
    else:
        assert False, p['tddr_mux_config']

    if p['oddr_mux_config'] != 'none':
        p['QINIT'] = random.randint(0, 1)
        p['SRTYPE'] = verilog.quote(random.choice(('SYNC', 'ASYNC')))
        p['ODDR_CLK_EDGE'] = verilog.quote(
            random.choice((
                'OPPOSITE_EDGE',
                'SAME_EDGE',
            )))

        print(
            '''
    (* KEEP, DONT_TOUCH, LOC = "{ologic_loc}" *)
    ODDR #(
        .INIT({QINIT}),
        .SRTYPE({SRTYPE}),
        .DDR_CLK_EDGE({ODDR_CLK_EDGE})
    ) oddr_{site} (
        .C({cnet}),
        .D1({d1net}),
        .D2({d2net}),
        .CE({cenet}),
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
    '''.format(n_di=idx))

    # Always output a LUT6 to make placer happy.
    print(
        '''
        (* KEEP, DONT_TOUCH *)
        LUT6 dummy_lut();
        ''')

    for p in params:
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
