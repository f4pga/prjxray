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


def use_oserdese2(p, luts, connects, clocks):

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

    fast_clock = random.choice(clocks)
    slow_clock = random.choice(clocks)

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
        .CLK({}),'''.format(fast_clock)
    if p['CLKDIV_USED']:
        clk_connections += '''
        .CLKDIV({}),'''.format(slow_clock)

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
    clknet = luts.get_next_output_net()
    p['IS_CLK_INVERTED'] = 0

    if p['tddr_mux_config'] == 'direct':
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
        .DDR_CLK_EDGE({TDDR_CLK_EDGE}),
        .IS_C_INVERTED({IS_CLK_INVERTED})
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
        ''')

    print(
        '''
        wire clk0_0, clk0_90, clk0_0_bg, clk_0_90_bg;
        wire clk1_0, clk1_90, clk1_0_bg, clk_0_90_bg;
        wire clk2_0, clk2_90, clk2_0_bg, clk_0_90_bg;
        wire clkfb;
        PLLE2_BASE #(
            .BANDWIDTH("OPTIMIZED"),  // OPTIMIZED, HIGH, LOW
            .CLKFBOUT_MULT(8),        // Multiply value for all CLKOUT, (2-64)
            .CLKFBOUT_PHASE(0.0),     // Phase offset in degrees of CLKFB, (-360.000-360.000).
            .CLKIN1_PERIOD(10.0),      // Input clock period in ns to ps resolution (i.e. 33.333 is 30 MHz).
            // CLKOUT0_DIVIDE - CLKOUT5_DIVIDE: Divide amount for each CLKOUT (1-128)
            .CLKOUT0_DIVIDE(1),
            .CLKOUT1_DIVIDE(1),
            .CLKOUT2_DIVIDE(2),
            .CLKOUT3_DIVIDE(2),
            .CLKOUT4_DIVIDE(4),
            .CLKOUT5_DIVIDE(4),
            // CLKOUT0_DUTY_CYCLE - CLKOUT5_DUTY_CYCLE: Duty cycle for each CLKOUT (0.001-0.999).
            .CLKOUT0_DUTY_CYCLE(0.5),
            .CLKOUT1_DUTY_CYCLE(0.5),
            .CLKOUT2_DUTY_CYCLE(0.5),
            .CLKOUT3_DUTY_CYCLE(0.5),
            .CLKOUT4_DUTY_CYCLE(0.5),
            .CLKOUT5_DUTY_CYCLE(0.5),
            // CLKOUT0_PHASE - CLKOUT5_PHASE: Phase offset for each CLKOUT (-360.000-360.000).
            .CLKOUT0_PHASE(0.0),
            .CLKOUT1_PHASE(90.0),
            .CLKOUT2_PHASE(0.0),
            .CLKOUT3_PHASE(90.0),
            .CLKOUT4_PHASE(0.0),
            .CLKOUT5_PHASE(90.0),
            .DIVCLK_DIVIDE(1),        // Master division value, (1-56)
            .REF_JITTER1(0.0),        // Reference input jitter in UI, (0.000-0.999).
            .STARTUP_WAIT("FALSE")    // Delay DONE until PLL Locks, ("TRUE"/"FALSE")
       )
       PLLE2_inst (
            // Clock Outputs: 1-bit (each) output: User configurable clock outputs
            .CLKOUT0(clk0_0),   // 1-bit output: CLKOUT0
            .CLKOUT1(clk0_90),   // 1-bit output: CLKOUT1
            .CLKOUT2(clk1_0),   // 1-bit output: CLKOUT2
            .CLKOUT3(clk1_90),   // 1-bit output: CLKOUT3
            .CLKOUT4(clk2_0),   // 1-bit output: CLKOUT4
            .CLKOUT5(clk2_90),   // 1-bit output: CLKOUT5
            // Feedback Clocks: 1-bit (each) output: Clock feedback ports
            .CLKFBOUT(clkfb), // 1-bit output: Feedback clock
            .LOCKED(),     // 1-bit output: LOCK
            .CLKIN1(),     // 1-bit input: Input clock
            // Control Ports: 1-bit (each) input: PLL control ports
            .PWRDWN(1'b0),     // 1-bit input: Power-down
            .RST(1'b0),           // 1-bit input: Reset
            // Feedback Clocks: 1-bit (each) input: Clock feedback ports
            .CLKFBIN(clkfb)    // 1-bit input: Feedback clock
       );
       BUFG clk0_0_BUFG (
            .O(clk0_0_bg),
            .I(clk0_0)
       );
       BUFG clk0_90_BUFG (
            .O(clk0_90_bg),
            .I(clk0_90)
       );
       BUFG clk1_0_BUFG (
            .O(clk1_0_bg),
            .I(clk1_0)
       );
       BUFG clk1_90_BUFG (
            .O(clk1_90_bg),
            .I(clk1_90)
       );
       BUFG clk2_0_BUFG (
            .O(clk2_0_bg),
            .I(clk2_0)
       );
       BUFG clk2_90_BUFG (
            .O(clk2_90_bg),
            .I(clk2_90)
       );
    ''')

    clocks = ['clk0_0_bg', 'clk0_90_bg', 'clk1_0_bg', 'clk1_90_bg', 'clk2_0_bg', 'clk2_90_bg']

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
            use_oserdese2(p, luts, connects, clocks)
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
