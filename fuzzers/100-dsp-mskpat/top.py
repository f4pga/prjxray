import os
import random
import json
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import verilog
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
    data = {}
    data['instances'] = []

    print('module top();')

    sites = list(gen_sites())

    for (tile, site) in sites:
        synthesis = '(* KEEP, DONT_TOUCH, LOC = "%s" *)' % (site)
        module = 'DSP48E1'
        instance = 'INST_%s' % (site)
        ports = {}
        params = {}

        params['ADREG'] = fuzz((0, 1))
        params['ALUMODEREG'] = fuzz((0, 1))
        # AREG/BREG requires inputs to be connected when configured with a value
        # of 2, constraining to 0 and 1 for now.
        params['AREG'] = fuzz((0, 1))
        params['ACASCREG'] = params['AREG'] if params[
            'AREG'] == 0 or params['AREG'] == 1 else fuzz((1, 2))
        params['BREG'] = fuzz((0, 1))
        params['BCASCREG'] = params['BREG'] if params[
            'BREG'] == 0 or params['BREG'] == 1 else fuzz((1, 2))
        params['CARRYINREG'] = fuzz((0, 1))
        params['CARRYINSELREG'] = fuzz((0, 1))
        params['CREG'] = fuzz((0, 1))
        params['DREG'] = fuzz((0, 1))
        params['INMODEREG'] = fuzz((0, 1))
        params['OPMODEREG'] = fuzz((0, 1))
        params['PREG'] = fuzz((0, 1))
        params['A_INPUT'] = verilog.quote(fuzz(('DIRECT', 'CASCADE')))
        params['B_INPUT'] = verilog.quote(fuzz(('DIRECT', 'CASCADE')))
        params['USE_DPORT'] = verilog.quote(fuzz(('TRUE', 'FALSE')))
        params['USE_SIMD'] = verilog.quote(
            fuzz(('ONE48', 'TWO24', 'FOUR12')))
        params['USE_MULT'] = verilog.quote(
            'NONE' if params['USE_SIMD'] != verilog.quote('ONE48') else
            fuzz(('NONE', 'MULTIPLY', 'DYNAMIC')))
        params['MREG'] = 0 if params['USE_MULT'] == verilog.quote(
            'NONE') else fuzz((0, 1))
        params['AUTORESET_PATDET'] = verilog.quote(
            fuzz(('NO_RESET', 'RESET_MATCH', 'RESET_NOT_MATCH')))
        params['MASK'] = '48\'d%s' % fuzz(48)
        params['PATTERN'] = '48\'d%s' % fuzz(48)
        params['SEL_MASK'] = verilog.quote(
            fuzz(('MASK', 'C', 'ROUNDING_MODE1', 'ROUNDING_MODE2')))
        params['USE_PATTERN_DETECT'] = verilog.quote(
            fuzz(('NO_PATDET', 'PATDET')))

        verilog.instance(synthesis + ' ' + module, instance, ports, params)

        params['TILE'] = tile
        params['SITE'] = site

        data['instances'].append(params)

    with open('params.json', 'w') as fp:
        json.dump(data, fp)

    print("endmodule")


if __name__ == '__main__':
    run()
