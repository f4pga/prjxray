import os
import re
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray.db import Database

XY_RE = re.compile('^BUFHCE_X([0-9]+)Y([0-9]+)$')
BUFGCTRL_XY_RE = re.compile('^BUFGCTRL_X([0-9]+)Y([0-9]+)$')
"""
BUFHCE's can be driven from:

MMCME2_ADV
BUFHCE
PLLE2_ADV
BUFGCTRL
"""


def get_xy(s):
    m = BUFGCTRL_XY_RE.match(s)
    x = int(m.group(1))
    y = int(m.group(2))
    return x, y


def gen_sites(desired_site_type):
    db = Database(util.get_db_root())
    grid = db.grid()

    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        for site, site_type in gridinfo.sites.items():
            if site_type == desired_site_type:
                yield site


def gen_bufhce_sites():
    db = Database(util.get_db_root())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        sites = []

        for site, site_type in gridinfo.sites.items():
            if site_type == 'BUFHCE':
                sites.append(site)

        if sites:
            yield tile_name, sorted(sites)


def read_site_to_cmt():
    with open(os.path.join(os.getenv('FUZDIR'), 'build',
                           'cmt_regions.csv')) as f:
        for l in f:
            site, cmt = l.strip().split(',')
            yield (site, cmt)


CMT_RE = re.compile('X([0-9]+)Y([0-9]+)')


class ClockSources(object):
    def __init__(self):
        self.sources = {}
        self.merged_sources = {}
        self.source_to_cmt = {}
        self.used_sources_from_cmt = {}

    def add_clock_source(self, source, cmt):
        if cmt not in self.sources:
            self.sources[cmt] = []

        self.sources[cmt].append(source)
        assert source not in self.source_to_cmt or self.source_to_cmt[
            source] == cmt, source
        self.source_to_cmt[source] = cmt

    def get_random_source(self, cmt):
        if cmt not in self.merged_sources:
            choices = []
            if 'ANY' in self.sources:
                choices.extend(self.sources['ANY'])

            if cmt in self.sources:
                choices.extend(self.sources[cmt])

            m = CMT_RE.match(cmt)
            x = int(m.group(1))
            y = int(m.group(2))

            if x % 2 == 0:
                x += 1
            else:
                x -= 1

            paired_cmt = 'X{}Y{}'.format(x, y)

            if paired_cmt in self.sources:
                choices.extend(self.sources[paired_cmt])

            self.merged_sources[cmt] = choices

        if self.merged_sources[cmt]:
            source = random.choice(self.merged_sources[cmt])

            source_cmt = self.source_to_cmt[source]
            if source_cmt not in self.used_sources_from_cmt:
                self.used_sources_from_cmt[source_cmt] = set()

            self.used_sources_from_cmt[source_cmt].add(source)

            if source_cmt != 'ANY' and len(
                    self.used_sources_from_cmt[source_cmt]) > 14:
                print('//', self.used_sources_from_cmt)
                self.used_sources_from_cmt[source_cmt].remove(source)
                return None
            else:
                return source


def check_allowed(mmcm_pll_dir, cmt):
    if mmcm_pll_dir == 'BOTH':
        return True
    elif mmcm_pll_dir == 'ODD':
        return (int(CMT_RE.match(cmt).group(1)) & 1) == 1
    elif mmcm_pll_dir == 'EVEN':
        return (int(CMT_RE.match(cmt).group(1)) & 1) == 0
    else:
        assert False, mmcm_pll_dir


def main():
    print('''
module top();
    ''')

    site_to_cmt = dict(read_site_to_cmt())

    clock_sources = ClockSources()

    mmcm_pll_only = random.randint(0, 1)
    mmcm_pll_dir = random.choice(('ODD', 'EVEN', 'BOTH'))

    if not mmcm_pll_only:
        for _ in range(2):
            clock_sources.add_clock_source('one', 'ANY')
            clock_sources.add_clock_source('zero', 'ANY')

    print("""
    wire zero = 0;
    wire one = 1;""")

    for idx in range(1):
        wire_name = "lut_wire_{}".format(idx)
        #clock_sources.add_clock_source(wire_name, 'ANY')
        print(
            """
    (* KEEP, DONT_TOUCH *)
    wire {wire_name};
    LUT6 lut{idx} (
        .O({wire_name})
        );""".format(
                idx=idx,
                wire_name=wire_name,
            ))

    for site in gen_sites('MMCME2_ADV'):
        mmcm_clocks = [
            'mmcm_clock_{site}_{idx}'.format(site=site, idx=idx)
            for idx in range(13)
        ]

        if not check_allowed(mmcm_pll_dir, site_to_cmt[site]):
            continue

        for clk in mmcm_clocks:
            clock_sources.add_clock_source(clk, site_to_cmt[site])

        print(
            """
    wire {c0}, {c1}, {c2}, {c3}, {c4}, {c5};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    MMCME2_ADV pll_{site} (
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

    for site in gen_sites('PLLE2_ADV'):
        pll_clocks = [
            'pll_clock_{site}_{idx}'.format(site=site, idx=idx)
            for idx in range(6)
        ]

        if not check_allowed(mmcm_pll_dir, site_to_cmt[site]):
            continue

        for clk in pll_clocks:
            clock_sources.add_clock_source(clk, site_to_cmt[site])

        print(
            """
    wire {c0}, {c1}, {c2}, {c3}, {c4}, {c5};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    PLLE2_ADV pll_{site} (
        .CLKOUT0({c0}),
        .CLKOUT1({c1}),
        .CLKOUT2({c2}),
        .CLKOUT3({c3}),
        .CLKOUT4({c4}),
        .CLKOUT5({c5})
    );
        """.format(
                site=site,
                c0=pll_clocks[0],
                c1=pll_clocks[1],
                c2=pll_clocks[2],
                c3=pll_clocks[3],
                c4=pll_clocks[4],
                c5=pll_clocks[5],
            ))

    for site in sorted(gen_sites("BUFGCTRL"), key=get_xy):
        wire_name = 'clk_{}'.format(site)

        if not mmcm_pll_only:
            clock_sources.add_clock_source(wire_name, 'ANY')

        print(
            """
    wire {wire_name};
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    BUFG bufg_{site} (
        .O({wire_name})
        );
        """.format(
                site=site,
                wire_name=wire_name,
            ))

    bufhce_sites = list(gen_bufhce_sites())
    for tile_name, sites in bufhce_sites:
        for site in sites:
            wire_name = clock_sources.get_random_source(site_to_cmt[site])
            if wire_name is None:
                continue

            print(
                """
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    BUFHCE buf_{site} (
        .I({wire_name})
    );
                    """.format(
                    site=site,
                    wire_name=wire_name,
                ))

    print("endmodule")


if __name__ == '__main__':
    main()
