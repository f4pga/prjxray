import json
import io
import os
import random
import math
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import lut_maker
from prjxray import verilog
from prjxray.db import Database

NOT_INCLUDED_TILES = ['LIOI3_SING', 'RIOI3_SING']

SITE_TYPES = ['OLOGICE3', 'ILOGICE3']

REGIONAL_CLOCK_BUFFERS = ['BUFHCE', 'BUFIO']
GLOBAL_CLOCK_BUFFERS = ['BUFGCTRL']
CLOCK_BUFFERS = REGIONAL_CLOCK_BUFFERS + GLOBAL_CLOCK_BUFFERS

MAX_REG_CLK_BUF = 2
MAX_GLB_CLK_BUF = 24
CUR_CLK = 0
MAX_ATTEMPTS = 50


def get_location(tile_name, divisor):
    y_location = int(tile_name.split("Y")[-1])

    if math.floor(y_location / divisor) % 2 == 0:
        # Location is on the bottom of the row/tile
        return "BOT"
    else:
        return "TOP"


def read_site_to_cmt():
    """ Yields clock sources and which CMT they route within. """
    with open(os.path.join(os.getenv('FUZDIR'), 'build',
                           'cmt_regions.csv')) as f:
        for l in f:
            site, cmt = l.strip().split(',')
            yield (site, cmt)


def gen_sites(site_types):
    '''
    Generates all sites belonging to `site_types` of
    a desired `tile`
    '''
    db = Database(util.get_db_root())
    grid = db.grid()

    tiles = grid.tiles()

    #Randomize tiles
    tiles_list = list(tiles)
    random.shuffle(tiles_list)

    for tile_name in tiles:
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        tile_type = gridinfo.tile_type

        for site_name, site_type in gridinfo.sites.items():
            if site_type in site_types:
                yield tile_type, tile_name, site_type, site_name


def generate_mmcm(site_to_cmt, clock_region):
    mmcm_clocks = None

    for _, _, _, site in gen_sites('MMCME2_ADV'):
        mmcm_region = site_to_cmt[site]

        if mmcm_region == clock_region:
            mmcm_clocks = [
                'mmcm_clock_{site}_{idx}'.format(site=site, idx=idx)
                for idx in range(3)
            ]

            print(
                """
        wire {c0}, {c1}, {c2};
        (* KEEP, DONT_TOUCH, LOC = "{site}" *)
        MMCME2_ADV mmcm_{site} (
        .CLKOUT0({c0}),
        .CLKOUT1({c1}),
        .CLKOUT2({c2})
        );""".format(
                    site=site,
                    c0=mmcm_clocks[0],
                    c1=mmcm_clocks[1],
                    c2=mmcm_clocks[2]))

    if not mmcm_clocks:
        return None

    return mmcm_clocks


def generate_glb_clk_buf(clock_regions, mmcm_clocks_dict):
    clk_buf_count = 0

    clock_signals = []

    for tile_type, _, site_type, site_name in gen_sites(GLOBAL_CLOCK_BUFFERS):

        if clk_buf_count >= MAX_GLB_CLK_BUF:
            break

        clock_signal = "buf_clk_{site}".format(site=site_name)

        if site_type == 'BUFGCTRL':
            mmcm_clocks = []

            for clock_region in clock_regions:
                # BUFGCTRL must have the clock coming from the same fabric row
                if ('Y0' in clock_region and tile_type == 'CLK_BUFG_BOT_R'
                    ) or ('Y0' not in clock_region
                          and tile_type == 'CLK_BUFG_TOP_R'):
                    mmcm_clocks = mmcm_clocks_dict[clock_region]
                    break

            assert mmcm_clocks, "No clock can be produced. Buffer not instantiated"

            print(
                '''
    wire {clk_out};

    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    BUFG buf_{site} (.I({clk_in}), .O({clk_out}));'''.format(
                    clk_in=random.choice(mmcm_clocks),
                    clk_out=clock_signal,
                    site=site_name))

        else:
            assert False, "The site is somehow corrupted"

        clk_buf_count += 1

        clock_signals.append(clock_signal)

    return clock_signals


def generate_reg_clk_buf(site_to_cmt, clock_region, mmcm_clocks, buf_type):
    clk_buf_count = 0
    clock_signals = []

    for tile_type, _, site_type, site_name in gen_sites(
            REGIONAL_CLOCK_BUFFERS):
        buf_region = site_to_cmt[site_name]

        if clk_buf_count >= MAX_REG_CLK_BUF:
            break

        if buf_type != site_type:
            continue

        if buf_region != clock_region:
            continue

        clock_signal = "buf_clk_{site}".format(site=site_name)

        if site_type == 'BUFR':
            print(
                '''
    wire {clk_out};

    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    BUFR buf_{site} (.I({clk_in}), .O({clk_out}));'''.format(
                    clk_in=random.choice(mmcm_clocks),
                    clk_out=clock_signal,
                    site=site_name))

        elif site_type == 'BUFIO':
            print(
                '''
    wire {clk_out};

    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    BUFIO buf_{site} (.I({clk_in}), .O({clk_out}));'''.format(
                    clk_in=random.choice(mmcm_clocks),
                    clk_out=clock_signal,
                    site=site_name))

        elif site_type == 'BUFHCE':
            print(
                '''
    wire {clk_out};

    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    BUFH buf_{site} (.I({clk_in}), .O({clk_out}));'''.format(
                    clk_in=random.choice(mmcm_clocks),
                    clk_out=clock_signal,
                    site=site_name))

        else:
            assert False, "The site is somehow corrupted"

        clk_buf_count += 1

        clock_signals.append(clock_signal)

    return clock_signals


def get_clock_signal(clock_signals, clock_types):
    '''
    Get a unique clock signals for a specific tile.
    '''
    global CUR_CLK

    clock_signal_string = ''
    is_first_clock = True

    for clock_type in clock_types:
        if random.choice([True, True, False]):
            continue

        clock_signal = clock_signals[CUR_CLK]
        if is_first_clock:
            clock_signal_string += '''
        .{}({})'''.format(clock_type, clock_signal)
        else:
            clock_signal_string += ''',
        .{}({})'''.format(clock_type, clock_signal)

        is_first_clock = False

        CUR_CLK = (CUR_CLK + 1) % MAX_GLB_CLK_BUF

    return clock_signal_string


def run():

    global CUR_CLK
    # One buffer type for each specimen
    buf_type = random.choice(GLOBAL_CLOCK_BUFFERS)

    site_location = random.choice(['TOP', 'BOT'])

    site_to_cmt = dict(read_site_to_cmt())
    clock_regions = list(dict.fromkeys(site_to_cmt.values()))

    print("module top();")

    clock_mmcm_dict = {}
    clock_signals_dict = {}
    site_types_dict = {}

    # Generate MMCM Clock generator
    for clock_region in clock_regions:
        mmcm_clocks = generate_mmcm(site_to_cmt, clock_region)

        if mmcm_clocks:
            clock_mmcm_dict[clock_region] = mmcm_clocks
            clock_signals_dict[clock_region] = []

            if buf_type in REGIONAL_CLOCK_BUFFERS:
                clock_signals_dict[clock_region] = generate_reg_clk_buf(
                    site_to_cmt, clock_region, mmcm_clocks, buf_type)
        else:
            clock_regions.remove(clock_region)

    if buf_type in GLOBAL_CLOCK_BUFFERS:
        clock_signals = generate_glb_clk_buf(clock_regions, clock_mmcm_dict)

        for clock_region in clock_regions:
            clock_signals_dict[clock_region] = clock_signals
            site_types_dict[clock_region] = random.choice(SITE_TYPES)

    half_column_used_clocks = {}

    for tile_type, tile_name, site_type, site_name in gen_sites(SITE_TYPES):
        if tile_type in NOT_INCLUDED_TILES:
            continue

        if random.choice([True, True, False]):
            continue

        site_region = site_to_cmt[site_name]

        if site_type != site_types_dict[site_region]:
            continue

        clock_signals = clock_signals_dict[site_region]

        bot_or_top = get_location(site_name, 1)

        half_column = '{}_{}'.format(site_region, get_location(tile_name, 25))

        if half_column not in half_column_used_clocks:
            half_column_used_clocks[half_column] = {
                'TOP': {
                    'ILOGIC':
                    get_clock_signal(clock_signals, ['CLK', 'CLKB', 'CLKDIV']),
                    'OLOGIC':
                    get_clock_signal(clock_signals, ['CLK', 'CLKDIV'])
                },
                'BOT': {
                    'ILOGIC':
                    get_clock_signal(clock_signals, ['CLK', 'CLKB', 'CLKDIV']),
                    'OLOGIC':
                    get_clock_signal(clock_signals, ['CLK', 'CLKDIV'])
                }
            }

        if site_type == 'ILOGICE3':
            print(
                '''
    (* KEEP, DONT_TOUCH, LOC = "{site_name}" *)
    ISERDESE2 #(
        .DATA_RATE("SDR")
    ) iserdes_{site_name} ({clk});'''.format(
                    site_name=site_name,
                    clk=half_column_used_clocks[half_column][bot_or_top]
                    ['ILOGIC']))
        elif site_type == 'OLOGICE3':
            print(
                '''
    (* KEEP, DONT_TOUCH, LOC = "{site_name}" *)
    OSERDESE2 #(
        .DATA_RATE_OQ("SDR"),
        .DATA_RATE_TQ("SDR")
    ) oserdes_{site_name} ({clk});'''.format(
                    site_name=site_name,
                    clk=half_column_used_clocks[half_column][bot_or_top]
                    ['OLOGIC']))

    print("endmodule")


if __name__ == '__main__':
    run()
