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


def run():
    tile_types = [
        'IBUF', 'OBUF', 'IOBUF_INTERMDISABLE', None, None, None, None, None
    ]

    i_idx = 0
    o_idx = 0
    io_idx = 0

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
    for tile, site in gen_sites():
        p = {}
        p['tile'] = tile
        p['site'] = site
        p['type'] = random.choice(tile_types)
        p['IOSTANDARD'] = verilog.quote(iostandard)
        p['PULLTYPE'] = verilog.quote(random.choice(pulls))

        if p['type'] is None:
            p['pad_wire'] = None
        elif p['type'] == 'IBUF':
            p['pad_wire'] = 'di[{}]'.format(i_idx)
            p['IDELAY_ONLY'] = random.randint(0, 1)
            if not p['IDELAY_ONLY']:
                p['owire'] = luts.get_next_input_net()
            else:
                p['owire'] = 'idelay_{site}'.format(**p)

            p['DRIVE'] = None
            p['SLEW'] = None
            p['IBUF_LOW_PWR'] = random.randint(0, 1)

            i_idx += 1
        elif p['type'] == 'OBUF':
            p['pad_wire'] = 'do[{}]'.format(o_idx)
            p['iwire'] = luts.get_next_output_net()
            p['DRIVE'] = random.choice(drives)
            p['SLEW'] = verilog.quote(random.choice(slews))

            o_idx += 1
        elif p['type'] == 'IOBUF_INTERMDISABLE':
            p['pad_wire'] = 'dio[{}]'.format(io_idx)
            p['iwire'] = luts.get_next_output_net()
            p['owire'] = luts.get_next_input_net()
            p['DRIVE'] = random.choice(drives)
            p['SLEW'] = verilog.quote(random.choice(slews))
            p['tristate_wire'] = random.choice(
                ('0', luts.get_next_output_net()))
            p['ibufdisable_wire'] = random.choice(
                ('0', luts.get_next_output_net()))
            p['intermdisable_wire'] = random.choice(
                ('0', luts.get_next_output_net()))
            io_idx += 1

        params.append(p)

        if p['type'] is not None:
            tile_params.append(
                (
                    tile, site, p['pad_wire'], iostandard, p['DRIVE'],
                    verilog.unquote(p['SLEW']) if p['SLEW'] else None,
                    verilog.unquote(p['PULLTYPE'])))

    write_params(tile_params)

    print(
        '''
`define N_DI {n_di}
`define N_DO {n_do}
`define N_DIO {n_dio}

module top(input wire [`N_DI-1:0] di, output wire [`N_DO-1:0] do, inout wire [`N_DIO-1:0] dio);
        (* KEEP, DONT_TOUCH *)
        IDELAYCTRL();
    '''.format(n_di=i_idx, n_do=o_idx, n_dio=io_idx))

    # Always output a LUT6 to make placer happy.
    print('''
        (* KEEP, DONT_TOUCH *)
        LUT6 dummy_lut();''')

    for p in params:
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

        elif p['type'] == 'OBUF':
            print(
                '''
        (* KEEP, DONT_TOUCH *)
        OBUF #(
            .IOSTANDARD({IOSTANDARD}),
            .DRIVE({DRIVE}),
            .SLEW({SLEW})
        ) ibuf_{site} (
            .O({pad_wire}),
            .I({iwire})
            );'''.format(**p),
                file=connects)
        elif p['type'] == 'IOBUF_INTERMDISABLE':
            print(
                '''
        (* KEEP, DONT_TOUCH *)
        IOBUF_INTERMDISABLE #(
            .IOSTANDARD({IOSTANDARD}),
            .DRIVE({DRIVE}),
            .SLEW({SLEW})
        ) ibuf_{site} (
            .IO({pad_wire}),
            .I({iwire}),
            .O({owire}),
            .T({tristate_wire}),
            .IBUFDISABLE({ibufdisable_wire}),
            .INTERMDISABLE({intermdisable_wire})
            );'''.format(**p),
                file=connects)

    for l in luts.create_wires_and_luts():
        print(l)

    print(connects.getvalue())

    print("endmodule")

    with open('params.jl', 'w') as f:
        json.dump(params, f, indent=2)


if __name__ == '__main__':
    run()
