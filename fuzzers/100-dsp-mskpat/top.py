import os
import random
import csv
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray.db import Database


def gen_sites():
    db = Database(util.get_db_root())
    grid = db.grid()
    for tile in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile)
        gridinfo = grid.gridinfo_at_loc(loc)
        if gridinfo.tile_type in ['DSP_L', 'DSP_R']:
            for site in sorted(gridinfo.sites.keys()):
                if gridinfo.sites[site] == 'DSP48E1':
                    yield tile, site


def fuzz(*args):
    if len(args) == 1 and isinstance(args[0], int):
        # Argument indicates that we should generate a random integer with
        # args[0] number of bits.
        return random.getrandbits(args[0])
    else:
        # Otherwise make a random choice
        return random.choice(*args)


def run():
    # Attributes list:
    #   Attribute name
    #   Verilog parameter value prefix
    #   Arguments to `fuzz`
    #   Verilog parameter value suffix
    attributes = []
    attributes.append(('ADREG', '', (0, 1), ''))
    attributes.append(('ALUMODEREG', '', (0, 1), ''))
    # AREG/BREG requires inputs to be connected when configured with a value of
    # 2, contstraining to 0 and 1 for now.
    attributes.append(('AREG', '', (0, 1), ''))
    attributes.append(('BREG', '', (0, 1), ''))
    attributes.append(('CARRYINREG', '', (0, 1), ''))
    attributes.append(('CARRYINSELREG', '', (0, 1), ''))
    attributes.append(('CREG', '', (0, 1), ''))
    attributes.append(('DREG', '', (0, 1), ''))
    attributes.append(('INMODEREG', '', (0, 1), ''))
    attributes.append(('OPMODEREG', '', (0, 1), ''))
    attributes.append(('PREG', '', (0, 1), ''))
    attributes.append(('A_INPUT', '"', ('DIRECT', 'CASCADE'), '"'))
    attributes.append(('B_INPUT', '"', ('DIRECT', 'CASCADE'), '"'))
    attributes.append(('USE_DPORT', '"', ('TRUE', 'FALSE'), '"'))
    attributes.append(('USE_SIMD', '"', ('ONE48', 'TWO24', 'FOUR12'), '"'))
    attributes.append(
        (
            'AUTORESET_PATDET', '"',
            ('NO_RESET', 'RESET_MATCH', 'RESET_NOT_MATCH'), '"'))
    attributes.append(('MASK', '48\'d', (48), ''))
    attributes.append(('PATTERN', '48\'d', (48), ''))
    attributes.append(
        (
            'SEL_MASK', '"', ('MASK', 'C', 'ROUNDING_MODE1', 'ROUNDING_MODE2'),
            '"'))
    attributes.append(('SEL_PATTERN', '"', ('PATTERN', 'C'), '"'))
    attributes.append(
        ('USE_PATTERN_DETECT', '"', ('NO_PATDET', 'PATDET'), '"'))

    # CSV headings
    headings = []
    headings.append('TILE')
    headings.append('SITE')

    for attribute in attributes:
        headings.append(attribute[0])

        # ACASCREG dependent on AREG
        if attribute[0] == 'AREG':
            headings.append('ACASCREG')

        # BCASCREG dependent on BREG
        if attribute[0] == 'BREG':
            headings.append('BCASCREG')

        # USE_MULT dependent on USE_SIMD
        if attribute[0] == 'USE_SIMD':
            headings.append('USE_MULT')
            # MREG dependent on USE_MULT
            headings.append('MREG')

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
            print(
                '\t\t.{0}({1}{2}{3}),'.format(attr[0], attr[1], val, attr[3]))

            # ACASCREG dependent on AREG
            if attr[0] == 'AREG':
                if val == 0 or val == 1:
                    print('\t\t.ACASCREG({0}),'.format(val))
                elif val == 2:
                    val = fuzz((1, 2))
                    print('\t\t.ACASCREG({0}),'.format(val))

                row.append(val)

            # BCASCREG dependent on BREG
            elif attr[0] == 'BREG':
                if val == 0 or val == 1:
                    print('\t\t.BCASCREG({0}),'.format(val))
                elif val == 2:
                    val = fuzz((1, 2))
                    print('\t\t.BCASCREG({0}),'.format(val))

                row.append(val)

            # USE_MULT dependent on USE_SIMD
            elif attr[0] == 'USE_SIMD':
                if val != "ONE48":
                    val = 'NONE'
                    print('\t\t.USE_MULT("{0}"),'.format(val))
                else:
                    val = fuzz(('NONE', 'MULTIPLY', 'DYNAMIC'))
                    print('\t\t.USE_MULT("{0}"),'.format(val))

                row.append(val)

                # MREG dependent on USE_MULT
                if val == 'NONE':
                    val = 0
                    print('\t\t.MREG("{0}"),'.format(val))
                else:
                    val = fuzz((0, 1))
                    print('\t\t.MREG("{0}"),'.format(val))

                row.append(val)

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
