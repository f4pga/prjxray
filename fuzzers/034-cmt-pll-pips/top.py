""" """
import os
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray.db import Database


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
    db = Database(util.get_db_root())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site_name, site_type in gridinfo.sites.items():
            if site_type in ['PLLE2_ADV']:
                phasers = find_phasers_for_pll(grid, loc)
                yield tile_name, site_name, phasers


def get_random_route_from_site_pin(db, tile_name, site_name, site_pin, direction, occupied_wires):

    grid = db.grid()
    tile = db.tilegrid[tile_name]
    tile_type = tile["type"]
    site_type = tile["sites"][site_name]

    tile = db.get_tile_type(tile_type)
    site = [s for s in tile.get_sites() if s.type == site_type][0] # FIXME: find correct site by vivado loc

    # Find site wire
    wire = None
    for pin in site.site_pins:
        if pin.name == site_pin:
            wire = pin.wire
            break
    assert wire is not None

    # Walk randomly over not occupied wires.
    route = []
    while True:
        route.append(wire)

        wires = []

        for pip in tile.pips:
            if direction == "down" and pip.net_from == wire:
                next_wire = pip.net_to
            elif direction == "up" and pip.net_to == wire:
                next_wire = pip.net_from
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
    print(
        '''
module top();
    (* KEEP, DONT_TOUCH *)
    LUT6 dummy();
    ''')

    db = Database(util.get_db_root())
    bufg_count = 0

    routes_file = open('routes.txt', 'w')

    for tile, site, phasers in sorted(gen_sites(), key=lambda x: x[0]):

        # Generate random routes to/from some pins
        routes = {}
        endpoints = {}

        pins = [
#            ('CLKIN1', 'up'),
#            ('CLKIN2', 'up'),
            ('CLKFBIN', 'up'),
            ('CLKFBOUT', 'down'),
#            ('CLKOUT0', 'down'),
#            ('CLKOUT1', 'down'),
#            ('CLKOUT2', 'down'),
#            ('CLKOUT3', 'down'),
        ]

        occupied_wires = set()
        for pin, dir in pins:

            route = get_random_route_from_site_pin(db, tile, site, pin, dir, occupied_wires)
            if route is None:
                endpoints[pin] = ""
                continue

            routes[pin] = (route, dir,)
            endpoints[pin] = route[-1] if dir == 'down' else route[0]

        internal_feedback = endpoints['CLKFBOUT'].endswith('CLKFBIN')
        if internal_feedback:            
            del routes['CLKFBIN']

        # Store them in random order so the TCL script will try to route
        # in random order.
        lines = []
        for pin, (route, dir,) in routes.items():

            route_str = " ".join(route)
            lines.append('{} {} {} {} {}\n'.format(tile, site, pin, dir, route_str))

        random.shuffle(lines)
        routes_file.writelines(lines)

        #clkfbin_src = random.choice(('BUFH', '0', '1', 'logic', None))
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
            drive_phaser = random.randint(0, 1)

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
            print("""
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
            elif clkfbin_src == '0':
                print("""
                assign clkfbin_{site} = 1'b0;
                """.format(site=site))
            elif clkfbin_src == '1':
                print("""
                assign clkfbin_{site} = 1'b1;
                """.format(site=site))
            elif clkfbin_src is None:
                pass
            elif clkfbin_src == 'logic':
                print("""
                (* KEEP, DONT_TOUCH *)
                LUT6 # (.INIT(64'h5555555555555555))
                clkfbin_logic_{site} (
                    .I0(clkfbout_mult_{site}),
                    .O(clkfbin_{site})
                );
                """.format(site=site))

        clkin_is_none = False

        for clkin in range(2):
            clkin_src = random.choice((
                'BUFH',
                'BUFR',
#                '0',
#                '1',
                'logic',
#                None,
            ))
            if clkin == 1 and clkin_is_none and clkin_src is None:
                clkin_src = 'BUFH'

            if clkin_src is None:
                pass
            elif clkin_src == 'BUFH':
                print(
                    """
                (* KEEP, DONT_TOUCH *)
                BUFH (
                    .O(clkin{idx}_{site})
                );""".format(idx=clkin + 1, site=site))
            elif clkin_src == 'BUFR':
                print(
                    """
                (* KEEP, DONT_TOUCH *)
                BUFR (
                    .O(clkin{idx}_{site})
                );""".format(idx=clkin + 1, site=site))
            elif clkin_src == '0':
                print(
                    """
                assign clkin{idx}_{site} = 0;
                """.format(idx=clkin + 1, site=site))
            elif clkin_src == '1':
                print(
                    """
                assign clkin{idx}_{site} = 1;
                """.format(idx=clkin + 1, site=site))
            elif clkin_src == 'logic':
                print("""
                (* KEEP, DONT_TOUCH *)
                LUT6 # (.INIT(64'h5555555555555555))
                clkin{idx}_logic_{site} (
                    .O(clkin{idx}_{site})
                );
                """.format(idx=clkin + 1, site=site))
            else:
                assert False, clkin_src

    print("endmodule")


if __name__ == '__main__':
    main()
