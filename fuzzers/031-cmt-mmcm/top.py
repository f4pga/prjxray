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
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import verilog
from prjxray.db import Database
import json


def find_hclk_ref_wires_for_mmcm(grid, loc):
    tilename = grid.tilename_at_loc((loc[0], loc[1] - 17))
    gridinfo = grid.gridinfo_at_tilename(tilename)

    assert gridinfo.tile_type in ['HCLK_CMT_L', 'HCLK_CMT']

    # HCLK_CMT_MUX_OUT_FREQ_REF[0-3]
    wires = []
    for idx in range(4):
        wires.append('{}/HCLK_CMT_MUX_OUT_FREQ_REF{}'.format(tilename, idx))

    return wires


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        tile_type = tile_name.rsplit("_", 1)[0]

        for site_name, site_type in gridinfo.sites.items():
            if site_type in ['MMCME2_ADV']:
                hclk_wires = find_hclk_ref_wires_for_mmcm(grid, loc)
                yield tile_name, tile_type, site_name, hclk_wires


def gen_true_false(p):
    if random.random() <= p:
        return verilog.quote("TRUE")
    else:
        return verilog.quote("FALSE")


def main():
    sites = sorted(list(gen_sites()))
    max_sites = len(sites)

    f = open('params.jl', 'w')
    f.write('module,loc,params\n')

    routes_file = open('routes.txt', 'w')

    print(
        """
module top(
    input [{N}:0] clkin1,
    input [{N}:0] clkin2,
    input [{N}:0] clkfb,
    input [{N}:0] dclk
);

    (* KEEP, DONT_TOUCH *)
    LUT1 dummy();
""".format(N=max_sites - 1))

    for i, (tile_name, tile_type, site,
            hclk_wires) in enumerate(sorted(gen_sites())):
        params = {
            "site":
            site,
            'active':
            random.random() > .2,
            "clkin1_conn":
            random.choice(
                ("clkfbout_mult_BUFG_" + site, "clkin1[{}]".format(i), "")),
            "clkin2_conn":
            random.choice(
                ("clkfbout_mult_BUFG_" + site, "clkin2[{}]".format(i), "")),
            "dclk_conn":
            random.choice((
                "0",
                "dclk[{}]".format(i),
            )),
            "dwe_conn":
            random.choice((
                "",
                "1",
                "0",
                "dwe_" + site,
                "den_" + site,
            )),
            "den_conn":
            random.choice((
                "",
                "1",
                "0",
                "den_" + site,
            )),
            "daddr4_conn":
            random.choice((
                "0",
                "dwe_" + site,
            )),
            "IS_RST_INVERTED":
            random.randint(0, 1),
            "IS_PWRDWN_INVERTED":
            random.randint(0, 1),
            "IS_CLKINSEL_INVERTED":
            random.randint(0, 1),
            "IS_PSEN_INVERTED":
            random.randint(0, 1),
            "IS_PSINCDEC_INVERTED":
            random.randint(0, 1),
            "CLKFBOUT_MULT_F":
            random.randint(2, 4),
            "CLKOUT0_DIVIDE_F":
            random.randint(1, 128),
            "CLKOUT1_DIVIDE":
            random.randint(1, 128),
            "CLKOUT2_DIVIDE":
            random.randint(1, 128),
            "CLKOUT3_DIVIDE":
            random.randint(1, 128),
            "CLKOUT4_DIVIDE":
            random.randint(1, 128),
            "CLKOUT5_DIVIDE":
            random.randint(1, 128),
            "CLKOUT6_DIVIDE":
            random.randint(1, 128),
            "DIVCLK_DIVIDE":
            random.randint(1, 5),
            "CLKOUT0_DUTY_CYCLE":
            "0.500",
            "STARTUP_WAIT":
            verilog.quote('TRUE' if random.randint(0, 1) else 'FALSE'),
            "COMPENSATION":
            verilog.quote(
                random.choice((
                    'ZHOLD',
                    'BUF_IN',
                    'EXTERNAL',
                    'INTERNAL',
                ))),
            "BANDWIDTH":
            verilog.quote(random.choice((
                'OPTIMIZED',
                'HIGH',
                'LOW',
            ))),
            "SS_EN":
            gen_true_false(0.15),
        }

        # SS_EN requires BANDWIDTH to be LOW
        if verilog.unquote(params["SS_EN"]) == "TRUE":
            params["BANDWIDTH"] = verilog.quote("LOW")

        if verilog.unquote(params['COMPENSATION']) == 'ZHOLD':
            params['clkfbin_conn'] = random.choice(
                (
                    "",
                    "clkfbout_mult_BUFG_" + site,
                ))
        elif verilog.unquote(params['COMPENSATION']) == 'INTERNAL':
            params['clkfbin_conn'] = random.choice(
                (
                    "",
                    "clkfbout_mult_" + site,
                ))
        else:
            params['clkfbin_conn'] = random.choice(
                ("", "clkfb[{}]".format(i), "clkfbout_mult_BUFG_" + site))

        def get_clkin_wires(idx):
            wires = [
                "{tile}_CLKIN{idx}", "{tile}_FREQ_BB0", "{tile}_FREQ_BB1",
                "{tile}_FREQ_BB2", "{tile}_FREQ_BB3", "{tile}_CLK_IN{idx}_INT"
                "{tile}_CLK_IN{idx}_HCLK"
            ]
            return [
                tile_name + "/" + w.format(tile=tile_type, idx=idx)
                for w in wires
            ]

        params['clkin1_route'] = random.choice(get_clkin_wires(1) + hclk_wires)
        params['clkin2_route'] = random.choice(get_clkin_wires(2) + hclk_wires)

        params['clkfbin_route'] = random.choice(
            (
                "{}_CLKFBOUT2IN",
                "{}_FREQ_BB0",
                "{}_FREQ_BB1",
                "{}_FREQ_BB2",
                "{}_FREQ_BB3",
                "{}_CLK_IN3_INT",
                "{}_CLK_IN3_HCLK",
            )).format(tile_type)

        f.write('%s\n' % (json.dumps(params)))

        def make_ibuf_net(net):
            p = net.find('[')
            return net[:p] + '_IBUF' + net[p:]

        if params['clkin1_conn'] != "":
            net = params['clkin1_conn']
            if "[" in net and "]" in net:
                net = make_ibuf_net(net)
            wire = params['clkin1_route']
            routes_file.write('{} {}\n'.format(net, wire))

        if params['clkin2_conn'] != "":
            net = params['clkin2_conn']
            if "[" in net and "]" in net:
                net = make_ibuf_net(net)
            wire = params['clkin2_route']
            routes_file.write('{} {}\n'.format(net, wire))

        if params['clkfbin_conn'] != "" and\
           params['clkfbin_conn'] != ("clkfbout_mult_BUFG_" + site):
            net = params['clkfbin_conn']
            if "[" in net and "]" in net:
                net = make_ibuf_net(net)
            wire = '{}/{}'.format(tile_name, params['clkfbin_route'])
            routes_file.write('{} {}\n'.format(net, wire))

        if not params['active']:
            continue

        print(
            """

    wire den_{site};
    wire dwe_{site};

    LUT1 den_lut_{site} (
        .O(den_{site})
    );

    LUT1 dwe_lut_{site} (
        .O(dwe_{site})
    );

    wire clkfbout_mult_{site};
    wire clkfbout_mult_BUFG_{site};
    wire clkout0_{site};
    wire clkout1_{site};
    wire clkout2_{site};
    wire clkout3_{site};
    wire clkout4_{site};
    wire clkout5_{site};
    wire clkout6_{site};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    MMCME2_ADV #(
            .IS_RST_INVERTED({IS_RST_INVERTED}),
            .IS_PWRDWN_INVERTED({IS_PWRDWN_INVERTED}),
            .IS_CLKINSEL_INVERTED({IS_CLKINSEL_INVERTED}),
            .IS_PSEN_INVERTED({IS_PSEN_INVERTED}),
            .IS_PSINCDEC_INVERTED({IS_PSINCDEC_INVERTED}),
            .CLKOUT0_DIVIDE_F({CLKOUT0_DIVIDE_F}),
            .CLKOUT1_DIVIDE({CLKOUT1_DIVIDE}),
            .CLKOUT2_DIVIDE({CLKOUT2_DIVIDE}),
            .CLKOUT3_DIVIDE({CLKOUT3_DIVIDE}),
            .CLKOUT4_DIVIDE({CLKOUT4_DIVIDE}),
            .CLKOUT5_DIVIDE({CLKOUT5_DIVIDE}),
            .CLKOUT6_DIVIDE({CLKOUT6_DIVIDE}),
            .CLKFBOUT_MULT_F({CLKFBOUT_MULT_F}),
            .DIVCLK_DIVIDE({DIVCLK_DIVIDE}),
            .STARTUP_WAIT({STARTUP_WAIT}),
            .CLKOUT0_DUTY_CYCLE({CLKOUT0_DUTY_CYCLE}),
            .COMPENSATION({COMPENSATION}),
            .BANDWIDTH({BANDWIDTH}),
            .SS_EN({SS_EN}),
            .CLKIN1_PERIOD(10.0),
            .CLKIN2_PERIOD(10.0)
    ) pll_{site} (
            .CLKFBOUT(clkfbout_mult_{site}),
            .CLKOUT0(clkout0_{site}),
            .CLKOUT1(clkout1_{site}),
            .CLKOUT2(clkout2_{site}),
            .CLKOUT3(clkout3_{site}),
            .CLKOUT4(clkout4_{site}),
            .CLKOUT5(clkout5_{site}),
            .CLKOUT6(clkout6_{site}),
            .DRDY(),
            .LOCKED(),
            .DO(),
            .CLKFBIN({clkfbin_conn}),
            .CLKIN1({clkin1_conn}),
            .CLKIN2({clkin2_conn}),
            .CLKINSEL(),
            .DCLK({dclk_conn}),
            .DEN({den_conn}),
            .DWE({dwe_conn}),
            .PWRDWN(),
            .RST(),
            .DI(),
            .DADDR({{7{{ {daddr4_conn} }} }}));

    (* KEEP, DONT_TOUCH *)
    BUFG bufg_{site} (
        .I(clkfbout_mult_{site}),
        .O(clkfbout_mult_BUFG_{site})
    );

    (* KEEP, DONT_TOUCH *)
    FDRE reg_clkfbout_mult_{site} (
        .C(clkfbout_mult_{site})
    );
            """.format(**params))

        disabled_clkout = random.randint(0, 7)
        for clk in range(0, 7):
            if clk == disabled_clkout:
                continue

            print(
                """
            (* KEEP, DONT_TOUCH *)
            FDRE reg_clkout{clk}_{site} (
                .C(clkout{clk}_{site})
            );
            """.format(clk=clk, site=params['site']))

    print('endmodule')

    f.close()


if __name__ == "__main__":
    main()
