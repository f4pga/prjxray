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
                yield site_name, phasers


def main():
    print(
        '''
module top();
    (* KEEP, DONT_TOUCH *)
    LUT6 dummy();
    ''')

    bufg_count = 0

    for site, phasers in sorted(gen_sites(), key=lambda x: x[0]):
        drive_feedback = random.randint(0, 1)
        clkfbin_src = random.choice(('BUFH', '0', '1', None))

        if drive_feedback:
            COMPENSATION = "INTERNAL"
        else:
            if clkfbin_src in ['0', '1']:
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

        drive_bufg = random.randint(0, 1) and bufg_count < 16

        if drive_bufg and clkfbin_src not in ['BUFH', 'BUFR']:
            bufg_count += 1
            print(
                """
            (* KEEP, DONT_TOUCH *)
            BUFG (
                .I(clkfbout_mult_{site})
            );""".format(site=site))

        if drive_feedback:
            print(
                """
            assign clkfbin_{site} = clkfbout_mult_{site};
            """.format(site=site))
        else:
            # If CLKFBIN is not using CLKFBOUT feedback, can be connected to:
            #  - BUFHCE/BUFR using dedicated path
            #  - Switch box clock port

            if clkfbin_src is None:
                pass
            elif clkfbin_src == 'BUFH':
                print(
                    """
                (* KEEP, DONT_TOUCH *)
                BUFH (
                    .I(clkfbout_mult_{site}),
                    .O(clkfbin_{site})
                );""".format(site=site))
            elif clkfbin_src == 'BUFR':
                print(
                    """
                (* KEEP, DONT_TOUCH *)
                BUFR (
                    .I(clkfbout_mult_{site}),
                    .O(clkfbin_{site})
                );""".format(site=site))
            elif clkfbin_src == '0':
                print(
                    """
                assign clkfbin_{site} = 0;
                """.format(site=site))
            elif clkfbin_src == '1':
                print(
                    """
                assign clkfbin_{site} = 1;
                """.format(site=site))
            else:
                assert False, clkfbin_src

        clkin_is_none = False

        for clkin in range(2):
            clkin_src = random.choice((
                'BUFH',
                'BUFR',
                '0',
                '1',
                None,
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
            else:
                assert False, clkfbin_src

    print("endmodule")


if __name__ == '__main__':
    main()
