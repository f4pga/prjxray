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
    """

    def __init__(self, limit=14):
        self.sources = {}
        self.source_to_cmt = {}
        self.used_sources_from_cmt = {}
        self.limit = limit

    def add_clock_source(self, source, cmt):
        """ Adds a source from a specific CMT.

        cmt='ANY' indicates that this source can be routed to any CMT.
        """
        if cmt not in self.sources:
            self.sources[cmt] = []

        self.sources[cmt].append(source)
        self.source_to_cmt[source] = cmt

    def get_random_source(self, cmt, no_repeats=False):
        """ Get a random source that is routable to the specific CMT.

        get_random_source will return a source that is either cmt='ANY',
        cmt equal to the input CMT, or the adjecent CMT.

        """

        choices = []

        if cmt in self.sources:
            choices.extend(self.sources[cmt])

        random.shuffle(choices)
        for source in choices:

            source_cmt = self.source_to_cmt[source]

            if source_cmt not in self.used_sources_from_cmt:
                self.used_sources_from_cmt[source_cmt] = set()

            if no_repeats and source in self.used_sources_from_cmt[source_cmt]:
                continue

            if len(self.used_sources_from_cmt[source_cmt]) >= self.limit:
                continue

            self.used_sources_from_cmt[source_cmt].add(source)
            return source

        return None


def main():
    """
    HCLK_IOI has the following inputs:

    12 (east) BUFH from the right side of the HROW
    12 (west) Bounce PIPs from one BUFH to any of 6 GCLK_BOT and 6 GCLK_TOP
    4 (east) PHSR_PERFCLK (IOCLK_PLL) from HCLK_CLB to input of BUFIO
    8 (4 north and 4 south) BUFR CLR and CE
    2 (south) I2IOCLK to input of BUFR
    2 (north) I2IOCLK to input of BUFR
    2 RCLK IMUX (IMUX0 and IMUX1) choosing input of BUFR

    outputs:
    4 (east) BUFRCLK - from BUFR to HROW
    4 (north) BUFR2IO - from BUFR
    4 (north) IOCLK from BUFIO

    """

    global_clock_sources = ClockSources()
    cmt_clock_sources = ClockSources()
    cmt_fast_clock_sources = ClockSources(4)
    bufr_clock_sources = ClockSources()
    bufio_clock_sources = ClockSources()
    site_to_cmt = dict(read_site_to_cmt())
    clock_region_limit = dict()
    clock_region_serdes_location = dict()

    db = Database(util.get_db_root())
    grid = db.grid()

    def gen_sites(desired_site_type):
        for tile_name in sorted(grid.tiles()):
            loc = grid.loc_of_tilename(tile_name)
            gridinfo = grid.gridinfo_at_loc(loc)
            for site, site_type in gridinfo.sites.items():
                if site_type == desired_site_type:
                    yield tile_name, site

    def serdes_relative_location(tile, site):
        (serdes_loc_x, serdes_loc_y) = grid.loc_of_tilename(tile)
        serdes_clk_reg = site_to_cmt[site]
        for tile_name in sorted(grid.tiles()):
            if 'HCLK_IOI3' in tile_name:
                (hclk_tile_loc_x,
                 hclk_tile_loc_y) = grid.loc_of_tilename(tile_name)
                if hclk_tile_loc_x == serdes_loc_x:
                    gridinfo = grid.gridinfo_at_loc(
                        (hclk_tile_loc_x, hclk_tile_loc_y))
                    random_site = next(iter(gridinfo.sites.keys()))
                    hclk_clk_reg = site_to_cmt[random_site]
                    if hclk_clk_reg == serdes_clk_reg:
                        if serdes_loc_y < hclk_tile_loc_y:
                            return "TOP"
                        elif serdes_loc_y > hclk_tile_loc_y:
                            return "BOTTOM"
                        else:
                            assert False

    clock_region_sites = set()

    def get_clock_region_site(site_type, clk_reg):
        for site_name, reg in site_to_cmt.items():
            if site_name.startswith(site_type) and reg in clk_reg:
                if site_name not in clock_region_sites:
                    clock_region_sites.add(site_name)
                    return site_name

    print(
        '''
module top();
    (* KEEP, DONT_TOUCH *)
    LUT6 dummy();
    ''')

    luts = LutMaker()
    bufs = StringIO()

    for _, site in gen_sites('MMCME2_ADV'):
        mmcm_clocks = [
            'mmcm_clock_{site}_{idx}'.format(site=site, idx=idx)
            for idx in range(13)
        ]

        for idx, clk in enumerate(mmcm_clocks):
            if idx < 4:
                cmt_fast_clock_sources.add_clock_source(clk, site_to_cmt[site])
            else:
                cmt_clock_sources.add_clock_source(clk, site_to_cmt[site])

        print(
            """
    wire cin1_{site}, cin2_{site}, clkfbin_{site}, {c0}, {c1}, {c2}, {c3}, {c4}, {c5};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    MMCME2_ADV pll_{site} (
        .CLKIN1(cin1_{site}),
        .CLKIN2(cin2_{site}),
        .CLKFBIN(clkfbin_{site}),
        .CLKOUT0({c0}),
        .CLKOUT0B({c4}),
        .CLKOUT1({c1}),
        .CLKOUT1B({c5}),
        .CLKOUT2({c2}),
        .CLKOUT2B({c6}),
        .CLKOUT3({c3}),
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

        for clk in pll_clocks:
            cmt_clock_sources.add_clock_source(clk, site_to_cmt[site])

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
    );""".format(site=site),
            file=bufs)
        global_clock_sources.add_clock_source(
            'O_{site}'.format(site=site), site_to_cmt[site])

    hclks_used_by_clock_region = {}
    for cmt in site_to_cmt.values():
        hclks_used_by_clock_region[cmt] = set()

    def check_hclk_src(src, src_cmt):
        if len(hclks_used_by_clock_region[src_cmt]
               ) >= 12 and src not in hclks_used_by_clock_region[src_cmt]:
            return None
        else:
            hclks_used_by_clock_region[src_cmt].add(src)
            return src

    cmt_clks_used_by_clock_region = {}
    for cmt in site_to_cmt.values():
        cmt_clks_used_by_clock_region[cmt] = list()

    def check_cmt_clk_src(src, src_clock_region):
        print(
            "//src: {}, clk_reg: {}, len {}".format(
                src, src_clock_region,
                len(cmt_clks_used_by_clock_region[src_clock_region])))
        if len(cmt_clks_used_by_clock_region[src_clock_region]) >= 4:
            return None
        else:
            cmt_clks_used_by_clock_region[src_clock_region].append(src)
            return src

    #Add IDELAYCTRL
    idelayctrl_in_clock_region = {}
    for cmt in site_to_cmt.values():
        idelayctrl_in_clock_region[cmt] = False
    for _, site in gen_sites('IDELAYCTRL'):
        if random.random() < 0.8:
            wire_name = global_clock_sources.get_random_source(
                site_to_cmt[site], no_repeats=False)
            if wire_name is None:
                continue
            src_cmt = global_clock_sources.source_to_cmt[wire_name]
            wire_name = check_hclk_src(wire_name, src_cmt)

            if wire_name is None:
                continue
            idelayctrl_in_clock_region[src_cmt] = True
            print(
                """
        assign I_{site} = {clock_source};
        (* KEEP, DONT_TOUCH, LOC = "{site}" *)
        IDELAYCTRL idelay_ctrl_{site} (
            .RDY(),
            .REFCLK(I_{site}),
            .RST()
            );""".format(site=site, clock_source=wire_name))

    print(bufs.getvalue())

    print("endmodule")


if __name__ == '__main__':
    main()
