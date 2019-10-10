import os
import random
import csv
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray.db import Database


def gen_sites ():
    db = Database(util.get_db_root())
    grid = db.grid()
    for tile in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile)
        gridinfo = grid.gridinfo_at_loc(loc)
        if gridinfo.tile_type in ['DSP_L', 'DSP_R']:
            for site in sorted(gridinfo.sites.keys()):
                if gridinfo.sites[site] == 'DSP48E1':
                    yield tile, site

def fuzz (*args):
    if len(args) == 1 and isinstance(args[0], int):
        # Argument indicates that we should generate a random integer with
        # args[0] number of bits.
        return random.getrandbits(args[0])
    else:
        # Otherwise make a random choice
        return random.choice(*args)

def run ():
    # Attributes list:
    #   Attribute name
    #   Verilog parameter value prefix
    #   Arguments to `fuzz`
    #   Verilog parameter value suffix
    attributes = []
    attributes.append(('A_INPUT', '"', ('DIRECT', 'CASCADE'), '"'))
    attributes.append(('B_INPUT', '"', ('DIRECT', 'CASCADE'), '"'))
    attributes.append(('AUTORESET_PATDET', '"',('NO_RESET', 'RESET_MATCH',
        'RESET_NOT_MATCH'), '"'))
    attributes.append(('MASK', '48\'d', (48), ''))
    attributes.append(('PATTERN', '48\'d', (48), ''))

    # CSV headings
    headings = []
    headings.append('TILE')
    headings.append('SITE')

    for attribute in attributes:
        headings.append(attribute[0])

    # CSV rows
    rows = []
    rows.append(headings)

    print('module top();')

    sites = list(gen_sites())

    # For every DSP site:
    #   Add an instance to top.v with fuzzed attributes
    #   Add a row for params.csv
    for (tile, site) in sites:
        row = []
        row.append(tile)
        row.append(site)
        print('\t(* KEEP, DONT_TOUCH, LOC = "{0}" *)'.format(site))
        print('\tDSP48E1 #(')

        for attr in attributes[:-1]:
            val = fuzz(attr[2])
            row.append(val)
            print('\t\t.{0}({1}{2}{3}),'.format(attr[0], attr[1], val, attr[3]))

        attr = attributes[-1]
        val = fuzz(attr[2])
        row.append(val)
        print('\t\t.{0}({1}{2}{3})'.format(attr[0], attr[1], val, attr[3]))

        rows.append(row)
        print('\t) dsp_{0} ();\n'.format(site))

    print("endmodule")

    # Generate params.csv
    with open('params.csv', 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(rows)
    writeFile.close()


if __name__ == '__main__':
    run()
