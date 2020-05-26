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
""" """
import os
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray.db import Database


class PipList(object):
    def __init__(self):
        self.piplist = {}
        self.ppiplist = {}

    def get_pip_and_ppip_list_for_tile_type(self, tile_type):

        # Load PIP list for the tile type if not already loaded
        if tile_type not in self.piplist:
            self.piplist[tile_type] = []

            fname = os.path.join(
                os.getenv('FUZDIR'), '..', 'piplist', 'build', 'cmt_top',
                tile_type.lower() + '.txt')

            with open(fname, "r") as f:
                for l in f:
                    tile, dst, src = l.strip().split('.')
                    if tile_type == tile:
                        self.piplist[tile_type].append((src, dst))

        # Load PPIP list for the tile type if not already loaded
        if tile_type not in self.ppiplist:
            self.ppiplist[tile_type] = []

            fname = os.path.join(
                os.getenv('FUZDIR'), '..', '071-ppips', 'build',
                'ppips_' + tile_type.lower() + '.db')

            with open(fname, "r") as f:
                for l in f:
                    pip_data, pip_type = l.strip().split()

                    if pip_type != 'always':
                        continue

                    tile, dst, src = pip_data.strip().split('.')
                    if tile_type == tile:
                        self.ppiplist[tile_type].append((src, dst))

        return self.piplist[tile_type], self.ppiplist[tile_type]


def find_phasers_for_pll(grid, loc):
    gridinfo = grid.gridinfo_at_loc((loc[0], loc[1] + 13))

    phasers = {
        'IN': [],
        'OUT': [],
    }

    for site_name, site_type in gridinfo.sites.items():
        if site_type == 'PHASER_IN_PHY':
            phasers['IN'].append(site_name)
        elif site_type == 'PHASER_OUT_PHY':
            phasers['OUT'].append(site_name)

    assert len(phasers['IN']) > 0
    assert len(phasers['OUT']) > 0

    phasers['IN'].sort()
    phasers['OUT'].sort()

    return phasers


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site_name, site_type in gridinfo.sites.items():
            if site_type in ['PLLE2_ADV']:
                phasers = find_phasers_for_pll(grid, loc)
                yield tile_name, site_name, phasers


def get_random_route_from_site_pin(
        pip_list, tile_name, site_pin, direction, occupied_wires):

    # A map of PLL site pins to wires they are connected to.
    pin_to_wire = {
        "CMT_TOP_L_UPPER_T": {
            "CLKIN1": "CMT_TOP_R_UPPER_T_PLLE2_CLKIN1",
            "CLKIN2": "CMT_TOP_R_UPPER_T_PLLE2_CLKIN2",
            "CLKFBIN": "CMT_TOP_R_UPPER_T_PLLE2_CLKFBIN",
        },
        "CMT_TOP_R_UPPER_T": {
            "CLKIN1": "CMT_TOP_R_UPPER_T_PLLE2_CLKIN1",
            "CLKIN2": "CMT_TOP_R_UPPER_T_PLLE2_CLKIN2",
            "CLKFBIN": "CMT_TOP_R_UPPER_T_PLLE2_CLKFBIN",
        },
    }

    # Get tile type
    tile_type = tile_name.rsplit("_", maxsplit=1)[0]

    # Get all PIPs (PIPs + PPIPs)
    pips, ppips = pip_list.get_pip_and_ppip_list_for_tile_type(tile_type)
    all_pips = pips + ppips

    # The first wire
    wire = pin_to_wire[tile_type][site_pin]

    # Walk randomly.
    route = []
    while True:
        route.append(wire)

        wires = []

        for src, dst in all_pips:
            if direction == "down" and src == wire:
                next_wire = dst
            elif direction == "up" and dst == wire:
                next_wire = src
            else:
                continue

            if next_wire not in occupied_wires:
                wires.append(next_wire)

        if len(wires) == 0:
            break

        wire = random.choice(wires)
        occupied_wires.add(wire)

    # For "up" direction reverse the route.
    if direction == "down":
        return route
    if direction == "up":
        return route[::-1]


def main():

    # 8 inputs per clock region
    # 5 clock regions for device
    max_clk_inputs = 8 * 5
    clkin_idx = 0

    print(
        '''
module top(
  input wire [{nclkin}:0] clkin
);

    (* KEEP, DONT_TOUCH *)
    LUT6 dummy();
    '''.format(nclkin=max_clk_inputs - 1))

    pip_list = PipList()
    bufg_count = 0

    design_file = open('design.txt', 'w')
    routes_file = open('routes.txt', 'w')

    for tile, site, phasers in sorted(gen_sites(), key=lambda x: x[0]):
        in_use = random.randint(0, 2) > 0

        design_file.write("{},{},{}\n".format(tile, site, int(in_use)))

        if not in_use:
            continue

        # Generate random routes to/from some pins
        routes = {}
        endpoints = {}

        pins = [
            ('CLKIN1', 'up'),
            ('CLKIN2', 'up'),
            ('CLKFBIN', 'up'),

            # Sometimes manually randomized route for CLKOUTx conflicts with
            # the verilog design.
            #('CLKOUT0', 'down'),
            #('CLKOUT1', 'down'),
            #('CLKOUT2', 'down'),
            #('CLKOUT3', 'down'),
        ]

        occupied_wires = set()
        for pin, dir in pins:

            route = get_random_route_from_site_pin(
                pip_list, tile, pin, dir, occupied_wires)
            if route is None:
                endpoints[pin] = ""
                continue

            routes[pin] = (
                route,
                dir,
            )
            endpoints[pin] = route[-1] if dir == 'down' else route[0]

        internal_feedback = endpoints['CLKFBIN'].endswith('CLKFBOUT')

        # Store them in a random order so the TCL script will try to route
        # them also in the random order.
        lines = []
        for pin, (
                route,
                dir,
        ) in routes.items():

            route_str = " ".join(route)
            lines.append(
                '{} {} {} {} {}\n'.format(tile, site, pin, dir, route_str))

        random.shuffle(lines)
        routes_file.writelines(lines)

        clkfbin_src = random.choice(('BUFH', 'logic'))

        if internal_feedback:
            COMPENSATION = "INTERNAL"
        else:
            if clkfbin_src == 'logic':
                COMPENSATION = 'EXTERNAL'
            else:
                COMPENSATION = "ZHOLD"

        print(
            """
    wire clkfbin_{site};
    wire clkin1_{site};
    wire clkin2_{site};
    wire clkfbout_mult_{site};
    wire clkout0_{site};
    wire clkout1_{site};
    wire clkout2_{site};
    wire clkout3_{site};
    wire clkout4_{site};
    wire clkout5_{site};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    PLLE2_ADV #(
        .COMPENSATION("{COMPENSATION}")
        ) pll_{site} (
            .CLKFBOUT(clkfbout_mult_{site}),
            .CLKOUT0(clkout0_{site}),
            .CLKOUT1(clkout1_{site}),
            .CLKOUT2(clkout2_{site}),
            .CLKOUT3(clkout3_{site}),
            .CLKOUT4(clkout4_{site}),
            .CLKOUT5(clkout5_{site}),
            .DRDY(),
            .LOCKED(),
            .DO(),
            .CLKFBIN(clkfbin_{site}),
            .CLKIN1(clkin1_{site}),
            .CLKIN2(clkin2_{site}),
            .CLKINSEL(),
            .DCLK(),
            .DEN(),
            .DWE(),
            .PWRDWN(),
            .RST(),
            .DI(),
            .DADDR());
            """.format(site=site, COMPENSATION=COMPENSATION))

        for clkout in range(4, 6):
            # CLKOUT4 and CLKOUT5 can only drive one signal type
            if random.randint(0, 1) and bufg_count < 16:
                bufg_count += 1
                print(
                    """
            (* KEEP, DONT_TOUCH *)
            BUFG (
                .I(clkout{idx}_{site})
            );""".format(idx=clkout, site=site))

        any_phaser = False

        for clkout in range(4):
            # CLKOUT0-CLKOUT3 can drive:
            #  - Global drivers (e.g. BUFG)
            #  - PHASER_[IN|OUT]_[CA|DB]_FREQREFCLK via BB_[0-3]
            drive_bufg = random.randint(0, 1) and bufg_count < 16
            drive_phaser = 0  #random.randint(0, 1)

            if drive_bufg:
                bufg_count += 1
                print(
                    """
            (* KEEP, DONT_TOUCH *)
            BUFG (
                .I(clkout{idx}_{site})
            );""".format(idx=clkout, site=site))

            if drive_phaser and not any_phaser and False:
                any_phaser = True
                print(
                    """
            (* KEEP, DONT_TOUCH, LOC="{phaser_loc}" *)
            PHASER_OUT phaser_{site}(
                .FREQREFCLK(clkout{idx}_{site})
            );""".format(idx=clkout, site=site, phaser_loc=phasers['OUT'][0]))

        if internal_feedback:
            print(
                """
                assign clkfbin_{site} = clkfbout_mult_{site};
                """.format(site=site))
        else:
            if clkfbin_src == 'BUFH':
                print(
                    """
                (* KEEP, DONT_TOUCH *)
                BUFH (
                    .I(clkfbout_mult_{site}),
                    .O(clkfbin_{site})
                );""".format(site=site))
            elif clkfbin_src == 'logic':
                print(
                    """
                (* KEEP, DONT_TOUCH *)
                LUT6 # (.INIT(64'h5555555555555555))
                clkfbin_logic_{site} (
                    .I0(clkfbout_mult_{site}),
                    .O(clkfbin_{site})
                );
                """.format(site=site))
            else:
                assert False, clkfb_src

        for clkin in range(2):
            clkin_src = random.choice((
                'BUFH',
                'BUFR',
                'logic',
            ))

            if clkin_src == 'BUFH':
                print(
                    """
                (* KEEP, DONT_TOUCH *)
                BUFH (
                    .O(clkin{idx}_{site}),
                    .I(clkin{idx2})
                );""".format(idx=clkin + 1, idx2=clkin_idx, site=site))
            elif clkin_src == 'BUFR':
                print(
                    """
                (* KEEP, DONT_TOUCH *)
                BUFR (
                    .O(clkin{idx}_{site}),
                    .I(clkin{idx2})
                );""".format(idx=clkin + 1, idx2=clkin_idx, site=site))
            elif clkin_src == 'logic':
                print(
                    """
                (* KEEP, DONT_TOUCH *)
                LUT6 # (.INIT(64'h5555555555555555))
                clkin{idx}_logic_{site} (
                    .I0(clkin{idx2}),
                    .O(clkin{idx}_{site})
                );
                """.format(idx=clkin + 1, idx2=clkin_idx, site=site))
            else:
                assert False, (clkin, clkin_src)

            clkin_idx += 1

    print("endmodule")


if __name__ == '__main__':
    main()
