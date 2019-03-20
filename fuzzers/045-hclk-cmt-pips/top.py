""" Emits top.v's for various BUFHCE routing inputs. """
import os
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray.lut_maker import LutMaker
from prjxray.db import Database
from io import StringIO

CMT_XY_FUN = util.create_xy_fun(prefix='')


def read_site_to_cmt():
    """ Yields clock sources and which CMT they route within. """
    with open(os.path.join(os.getenv('FUZDIR'), 'build',
                           'cmt_regions.csv')) as f:
        for l in f:
            site, cmt = l.strip().split(',')
            yield (site, cmt)


class ClockSources(object):
    """ Class for tracking clock sources.

    Some clock sources can be routed to any CMT, for these, cmt='ANY'.
    For clock sources that belong to a CMT, cmt should be set to the CMT of
    the source.

    """

    def __init__(self):
        self.sources = {}
        self.source_to_cmt = {}
        self.used_sources_from_cmt = {}

    def add_clock_source(self, source, cmt):
        """ Adds a source from a specific CMT.

        cmt='ANY' indicates that this source can be routed to any CMT.
        """
        if cmt not in self.sources:
            self.sources[cmt] = []

        self.sources[cmt].append(source)
        self.source_to_cmt[source] = cmt

    def get_random_source(
            self, cmt, uses_left_right_routing=False, no_repeats=False):
        """ Get a random source that is routable to the specific CMT.

        get_random_source will return a source that is either cmt='ANY',
        cmt equal to the input CMT, or the adjecent CMT.

        """

        choices = []

        if cmt in self.sources:
            choices.extend(self.sources[cmt])

        if uses_left_right_routing:
            x, y = CMT_XY_FUN(cmt)

            if x % 2 == 0:
                x += 1
            else:
                x -= 1

            paired_cmt = 'X{}Y{}'.format(x, y)

            if paired_cmt in self.sources:
                for source in self.sources[paired_cmt]:
                    if 'BUFHCE' not in source:
                        choices.append(source)

        random.shuffle(choices)

        if not uses_left_right_routing:
            return choices[0]

        for source in choices:

            source_cmt = self.source_to_cmt[source]

            if source_cmt not in self.used_sources_from_cmt:
                self.used_sources_from_cmt[source_cmt] = set()

            if no_repeats and source in self.used_sources_from_cmt[source_cmt]:
                continue

            if len(self.used_sources_from_cmt[source_cmt]) >= 14:
                continue

            self.used_sources_from_cmt[source_cmt].add(source)

            return source

        return None


def get_paired_iobs(db, grid, tile_name):
    """ The two IOB33M's above and below the HCLK row have dedicate clock lines.
    """

    gridinfo = grid.gridinfo_at_tilename(tile_name)
    loc = grid.loc_of_tilename(tile_name)

    if gridinfo.tile_type.endswith('_L'):
        inc = 1
        lr = 'R'
    else:
        inc = -1
        lr = 'L'

    idx = 1
    while True:
        gridinfo = grid.gridinfo_at_loc((loc.grid_x + inc * idx, loc.grid_y))

        if gridinfo.tile_type.startswith('HCLK_IOI'):
            break

        idx += 1

    # Move from HCLK_IOI column to IOB column
    idx += 1

    for dy in [-1, -3, 2, 4]:
        iob_loc = (loc.grid_x + inc * idx, loc.grid_y + dy)
        gridinfo = grid.gridinfo_at_loc(iob_loc)
        tile_name = grid.tilename_at_loc(iob_loc)

        assert gridinfo.tile_type.startswith(lr + 'IOB'), (
            gridinfo, lr + 'IOB')

        for site, site_type in gridinfo.sites.items():
            if site_type in ['IOB33M', 'IOB18M']:
                yield tile_name, site, site_type[-3:-1]


def check_allowed(mmcm_pll_dir, cmt):
    """ Check whether the CMT specified is in the allowed direction.

    This function is designed to bias sources to either the left or right
    input lines.

    """
    if mmcm_pll_dir == 'BOTH':
        return True
    elif mmcm_pll_dir == 'ODD':
        x, y = CMT_XY_FUN(cmt)
        return (x & 1) == 1
    elif mmcm_pll_dir == 'EVEN':
        x, y = CMT_XY_FUN(cmt)
        return (x & 1) == 0
    else:
        assert False, mmcm_pll_dir


def main():
    """
    HCLK_CMT switch box has the follow inputs:

    4 IOBs above and below
    14 MMCM outputs
    8 PLL outputs
    4 PHASER_IN outputs
    2 INT connections

    and the following outputs:

    3 PLLE2 inputs
    2 BUFMR inputs
    3 MMCM inputs
    ~2 MMCM -> BUFR???
    """

    clock_sources = ClockSources()
    adv_clock_sources = ClockSources()
    site_to_cmt = dict(read_site_to_cmt())

    db = Database(util.get_db_root())
    grid = db.grid()

    def gen_sites(desired_site_type):
        for tile_name in sorted(grid.tiles()):
            loc = grid.loc_of_tilename(tile_name)
            gridinfo = grid.gridinfo_at_loc(loc)
            for site, site_type in gridinfo.sites.items():
                if site_type == desired_site_type:
                    yield tile_name, site

    hclk_cmts = set()
    ins = []
    iobs = StringIO()

    hclk_cmt_tiles = set()
    for tile_name, site in gen_sites('BUFMRCE'):
        cmt = site_to_cmt[site]
        hclk_cmts.add(cmt)
        hclk_cmt_tiles.add(tile_name)

    mmcm_pll_only = random.randint(0, 1)
    mmcm_pll_dir = random.choice(('ODD', 'EVEN', 'BOTH'))

    print(
        '// mmcm_pll_only {} mmcm_pll_dir {}'.format(
            mmcm_pll_only, mmcm_pll_dir))

    for tile_name in sorted(hclk_cmt_tiles):
        for _, site, volt in get_paired_iobs(db, grid, tile_name):

            ins.append('input clk_{site}'.format(site=site))
            if check_allowed(mmcm_pll_dir, site_to_cmt[site]):
                clock_sources.add_clock_source(
                    'clock_IBUF_{site}'.format(site=site), site_to_cmt[site])
            adv_clock_sources.add_clock_source(
                'clock_IBUF_{site}'.format(site=site), site_to_cmt[site])

            print(
                """
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    wire clock_IBUF_{site};
    IBUF #( .IOSTANDARD("LVCMOS{volt}") ) ibuf_{site} (
        .I(clk_{site}),
        .O(clock_IBUF_{site})
        );
                    """.format(volt=volt, site=site),
                file=iobs)

    print(
        '''
module top({inputs});
    (* KEEP, DONT_TOUCH *)
    LUT6 dummy();
    '''.format(inputs=', '.join(ins)))

    print(iobs.getvalue())

    luts = LutMaker()
    wires = StringIO()
    bufhs = StringIO()

    for _, site in gen_sites('MMCME2_ADV'):
        mmcm_clocks = [
            'mmcm_clock_{site}_{idx}'.format(site=site, idx=idx)
            for idx in range(13)
        ]

        if check_allowed(mmcm_pll_dir, site_to_cmt[site]):
            for clk in mmcm_clocks:
                clock_sources.add_clock_source(clk, site_to_cmt[site])

        print(
            """
    wire cin1_{site}, cin2_{site}, clkfbin_{site}, {c0}, {c1}, {c2}, {c3}, {c4}, {c5};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    MMCME2_ADV pll_{site} (
        .CLKIN1(cin1_{site}),
        .CLKIN2(cin2_{site}),
        .CLKFBIN(clkfbin_{site}),
        .CLKOUT0({c0}),
        .CLKOUT0B({c1}),
        .CLKOUT1({c2}),
        .CLKOUT1B({c3}),
        .CLKOUT2({c4}),
        .CLKOUT2B({c5}),
        .CLKOUT3({c6}),
        .CLKOUT3B({c7}),
        .CLKOUT4({c8}),
        .CLKOUT5({c9}),
        .CLKOUT6({c10}),
        .CLKFBOUT({c11}),
        .CLKFBOUTB({c12})
    );
        """.format(
                site=site,
                c0=mmcm_clocks[0],
                c1=mmcm_clocks[1],
                c2=mmcm_clocks[2],
                c3=mmcm_clocks[3],
                c4=mmcm_clocks[4],
                c5=mmcm_clocks[5],
                c6=mmcm_clocks[6],
                c7=mmcm_clocks[7],
                c8=mmcm_clocks[8],
                c9=mmcm_clocks[9],
                c10=mmcm_clocks[10],
                c11=mmcm_clocks[11],
                c12=mmcm_clocks[12],
            ))

    for _, site in gen_sites('PLLE2_ADV'):
        pll_clocks = [
            'pll_clock_{site}_{idx}'.format(site=site, idx=idx)
            for idx in range(7)
        ]

        if check_allowed(mmcm_pll_dir, site_to_cmt[site]):
            for clk in pll_clocks:
                clock_sources.add_clock_source(clk, site_to_cmt[site])

        print(
            """
    wire cin1_{site}, cin2_{site}, clkfbin_{site}, {c0}, {c1}, {c2}, {c3}, {c4}, {c5}, {c6};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    PLLE2_ADV pll_{site} (
        .CLKIN1(cin1_{site}),
        .CLKIN2(cin2_{site}),
        .CLKFBIN(clkfbin_{site}),
        .CLKOUT0({c0}),
        .CLKOUT1({c1}),
        .CLKOUT2({c2}),
        .CLKOUT3({c3}),
        .CLKOUT4({c4}),
        .CLKOUT5({c5}),
        .CLKFBOUT({c6})
    );
        """.format(
                site=site,
                c0=pll_clocks[0],
                c1=pll_clocks[1],
                c2=pll_clocks[2],
                c3=pll_clocks[3],
                c4=pll_clocks[4],
                c5=pll_clocks[5],
                c6=pll_clocks[6],
            ))

    for tile_name, site in gen_sites('BUFHCE'):
        print(
            """
    wire I_{site};
    wire O_{site};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    BUFHCE buf_{site} (
        .I(I_{site}),
        .O(O_{site})
    );
                    """.format(site=site, ),
            file=bufhs)

        if site_to_cmt[site] in hclk_cmts:
            if not mmcm_pll_only:
                clock_sources.add_clock_source(
                    'O_{site}'.format(site=site), site_to_cmt[site])
            adv_clock_sources.add_clock_source(
                'O_{site}'.format(site=site), site_to_cmt[site])

    hclks_used_by_cmt = {}
    for cmt in site_to_cmt.values():
        hclks_used_by_cmt[cmt] = set()

    def check_hclk_src(src, src_cmt):
        if len(hclks_used_by_cmt[src_cmt]
               ) >= 12 and src not in hclks_used_by_cmt[src_cmt]:
            return None
        else:
            hclks_used_by_cmt[src_cmt].add(src)
            return src

    if random.random() > .10:
        for tile_name, site in gen_sites('BUFHCE'):
            wire_name = clock_sources.get_random_source(
                site_to_cmt[site],
                uses_left_right_routing=True,
                no_repeats=mmcm_pll_only)

            if wire_name is not None and 'BUFHCE' in wire_name:
                # Looping a BUFHCE to a BUFHCE requires using a hclk in the
                # CMT of the source
                src_cmt = clock_sources.source_to_cmt[wire_name]

                wire_name = check_hclk_src(wire_name, src_cmt)

            if wire_name is None:
                continue

            print(
                """
        assign I_{site} = {wire_name};""".format(
                    site=site,
                    wire_name=wire_name,
                ),
                file=bufhs)

    for tile_name, site in gen_sites('BUFMRCE'):
        pass

    for l in luts.create_wires_and_luts():
        print(l)

    print(wires.getvalue())
    print(bufhs.getvalue())

    for _, site in gen_sites('BUFR'):
        adv_clock_sources.add_clock_source(
            'O_{site}'.format(site=site), site_to_cmt[site])
        print(
            """
    wire O_{site};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    BUFR bufr_{site} (
        .O(O_{site})
        );""".format(site=site))

    for _, site in gen_sites('PLLE2_ADV'):
        for cin in ('cin1', 'cin2', 'clkfbin'):
            if random.random() > .2:
                src = adv_clock_sources.get_random_source(site_to_cmt[site])

                src_cmt = adv_clock_sources.source_to_cmt[src]

                if 'IBUF' not in src and 'BUFR' not in src:
                    # Clocks from input pins do not require HCLK's, all other
                    # sources route from a global row clock.
                    src = check_hclk_src(src, src_cmt)

                if src is None:
                    continue

                print(
                    """
        assign {cin}_{site} = {csrc};
            """.format(cin=cin, site=site, csrc=src))

    for _, site in gen_sites('MMCME2_ADV'):
        for cin in ('cin1', 'cin2', 'clkfbin'):
            if random.random() > .2:
                src = adv_clock_sources.get_random_source(site_to_cmt[site])

                src_cmt = adv_clock_sources.source_to_cmt[src]
                if 'IBUF' not in src and 'BUFR' not in src:
                    # Clocks from input pins do not require HCLK's, all other
                    # sources route from a global row clock.
                    src = check_hclk_src(src, src_cmt)

                if src is None:
                    continue

                print(
                    """
        assign {cin}_{site} = {csrc};
            """.format(cin=cin, site=site, csrc=src))

    print("endmodule")


if __name__ == '__main__':
    main()
