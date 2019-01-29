import os
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray.db import Database


def gen_sites():
    db = Database(util.get_db_root())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        if gridinfo.tile_type in ['DSP_L', 'DSP_R']:
            for site in sorted(gridinfo.sites.keys()):
                if gridinfo.sites[site] == 'DSP48E1':
                    yield tile_name, site


def write_params(lines):
    pinstr = 'tile,site,mask,pattern\n'
    for tile, site, mask, pattern in lines:
        pinstr += '%s,%s,%s,%s\n' % (tile, site, mask, pattern)

    open('params.csv', 'w').write(pinstr)


def run():
    print('''
module top();
    ''')

    lines = []

    sites = list(gen_sites())
    for (tile_name, site_name) in sites:
        mask = random.randint(0, 2**48 - 1)
        pattern = random.randint(0, 2**48 - 1)
        lines.append((tile_name, site_name, mask, pattern))

        print(
            '''
            (* KEEP, DONT_TOUCH, LOC = "{0}" *)
            DSP48E1 #(
                .MASK(48'h{1:x}),
                .PATTERN(48'h{2:x})
            ) dsp_{0} (
            );
'''.format(site_name, mask, pattern))

    print("endmodule")
    write_params(lines)


if __name__ == '__main__':
    run()
