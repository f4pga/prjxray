#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
import os
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray.db import Database

INT_TILE_TYPES = ['INT_L', 'INT_R']
HCLK_TILE_TYPES = ['HCLK_L', 'HCLK_R', 'HCLK_L_BOT_UTURN', 'HCLK_R_BOT_UTURN']


def get_int_column_roots(grid):
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        if gridinfo.tile_type not in INT_TILE_TYPES:
            continue

        next_gridinfo = grid.gridinfo_at_loc((loc.grid_x, loc.grid_y + 1))

        if next_gridinfo.tile_type in INT_TILE_TYPES:
            continue

        if next_gridinfo.tile_type in HCLK_TILE_TYPES:
            continue

        assert next_gridinfo.tile_type in [
            'B_TERM_INT', 'BRKH_INT', 'BRKH_B_TERM_INT'
        ], next_gridinfo.tile_type

        yield tile_name


def build_int_columns(grid):

    int_columns = {}

    for root_tile_name in get_int_column_roots(grid):
        assert root_tile_name not in int_columns
        int_columns[root_tile_name] = []

        tile_name = root_tile_name
        gridinfo = grid.gridinfo_at_tilename(tile_name)

        # Walk up INT column.
        while gridinfo.tile_type in INT_TILE_TYPES:
            int_columns[root_tile_name].append(tile_name)

            loc = grid.loc_of_tilename(tile_name)
            tile_name = grid.tilename_at_loc((loc.grid_x, loc.grid_y - 1))
            gridinfo = grid.gridinfo_at_tilename(tile_name)

            if gridinfo.tile_type in HCLK_TILE_TYPES:
                loc = grid.loc_of_tilename(tile_name)
                tile_name = grid.tilename_at_loc((loc.grid_x, loc.grid_y - 1))
                gridinfo = grid.gridinfo_at_tilename(tile_name)

        assert gridinfo.tile_type in [
            'T_TERM_INT', 'BRKH_INT', 'BRKH_TERM_INT'
        ], gridinfo.tile_type

    return int_columns


def pair_int_tiles(grid, int_tiles):
    tiles_left = set(int_tiles)

    while tiles_left:
        tile_name = tiles_left.pop()

        gridinfo = grid.gridinfo_at_tilename(tile_name)
        loc = grid.loc_of_tilename(tile_name)

        assert gridinfo.tile_type in INT_TILE_TYPES

        if gridinfo.tile_type == 'INT_L':
            other_int_tile = 'INT_R'
            other_loc = (loc.grid_x + 1, loc.grid_y)
        else:
            other_int_tile = 'INT_L'
            other_loc = (loc.grid_x - 1, loc.grid_y)

        paired_tile_name = grid.tilename_at_loc(other_loc)
        paired_gridinfo = grid.gridinfo_at_tilename(paired_tile_name)
        assert paired_gridinfo.tile_type == other_int_tile, paired_gridinfo.tile_type

        tiles_left.remove(paired_tile_name)

        yield sorted([tile_name, paired_tile_name])


def is_orphan_int_row(grid, int_l, int_r):
    """ Returns true if given INT pair have no adjcent sites. """

    loc = grid.loc_of_tilename(int_l)

    if grid.gridinfo_at_loc(
        (loc.grid_x - 1, loc.grid_y)).tile_type != 'INT_INTERFACE_L':
        return False

    if grid.gridinfo_at_loc(
        (loc.grid_x - 2, loc.grid_y)).tile_type != 'VFRAME':
        return False

    loc = grid.loc_of_tilename(int_r)

    if grid.gridinfo_at_loc(
        (loc.grid_x + 1, loc.grid_y)).tile_type != 'INT_INTERFACE_R':
        return False

    if grid.gridinfo_at_loc(
        (loc.grid_x + 2,
         loc.grid_y)).tile_type not in ['CLK_FEED', 'CLK_BUFG_REBUF', 'NULL']:
        return False

    return True


def gen_orphan_ints(grid):
    int_columns = build_int_columns(grid)

    for int_l_column, int_r_column in sorted(pair_int_tiles(
            grid, int_columns.keys())):
        found_site = False
        for int_l, int_r in zip(int_columns[int_l_column],
                                int_columns[int_r_column]):
            if not is_orphan_int_row(grid, int_l, int_r):
                found_site = True
                break

        if not found_site:
            yield int_columns[int_l_column], int_columns[int_r_column]


def write_params(params):
    pinstr = 'tile,val\n'
    for tile, (val) in sorted(params.items()):
        pinstr += '%s,%s\n' % (tile, val)
    open('params.csv', 'w').write(pinstr)


def build_cross_int(params, grid, int_l, int_r):
    """ Toggles INT_R.ER1BEG1.EE4END0 """

    loc = grid.loc_of_tilename(int_r)

    origin_tile = grid.tilename_at_loc((loc.grid_x - 4, loc.grid_y))
    origin_gridinfo = grid.gridinfo_at_tilename(origin_tile)
    assert origin_gridinfo.tile_type == 'CLBLL_R'
    origin_site = sorted(origin_gridinfo.sites.keys())[random.randint(0, 1)]

    dest_tile = grid.tilename_at_loc((loc.grid_x + 4, loc.grid_y))
    dest_gridinfo = grid.gridinfo_at_tilename(dest_tile)
    assert dest_gridinfo.tile_type == 'CLBLL_L'
    dest_site = sorted(dest_gridinfo.sites.keys())[0]

    dest2_tile = grid.tilename_at_loc((loc.grid_x + 4, loc.grid_y + 1))
    dest2_gridinfo = grid.gridinfo_at_tilename(dest2_tile)
    assert dest2_gridinfo.tile_type == 'CLBLL_L', dest2_gridinfo.tile_type
    dest2_site = sorted(dest2_gridinfo.sites.keys())[1]

    if random.randint(0, 1):
        dest_wire = 'origin_wire_{origin_site}'.format(origin_site=origin_site)
    else:
        dest_wire = '1'

    if random.randint(0, 1):
        dest_wire2 = 'origin_wire_{origin_site}'.format(
            origin_site=origin_site)
    else:
        dest_wire2 = '1'

    if random.randint(0, 1):
        dest_wire3 = 'origin_wire_{origin_site}'.format(
            origin_site=origin_site)
    else:
        dest_wire3 = '1'

    if random.randint(0, 1):
        dest_wire4 = 'origin_wire_{origin_site}'.format(
            origin_site=origin_site)
    else:
        dest_wire4 = '1'

    # origin_site.AQ -> dest_tile.D6 enables INT_R.ER1BEG1.EE4END0
    print(
        """
    // Force origin FF into A position with MUXF7_L and MUXF8
    wire origin_wire_{origin_site};

    wire f7_to_lo_{origin_site};
    wire lut_to_f7_{origin_site};
    (* KEEP, DONT_TOUCH, LOC = "{origin_site}" *)
    LUT6_L #(
    .INIT(0)
    ) lut_rom_{origin_site} (
            .I0(1),
            .I1(origin_wire_{origin_site}),
            .I2(0),
            .I3(1),
            .I4(1),
            .I5(1),
            .LO(lut_to_f7_{origin_site})
            );
    (* KEEP, DONT_TOUCH, LOC = "{origin_site}" *)
    MUXF7_D f7_{origin_site} (
        .I0(lut_to_f7_{origin_site}),
        .LO(f7_to_lo_{origin_site}),
        .O(origin_wire_{origin_site})
        );
    (* KEEP, DONT_TOUCH, LOC = "{origin_site}" *)
    MUXF8 f8_{origin_site} (
        .I1(f7_to_lo_{origin_site})
        );

    wire dest_wire_{dest_site};
    wire dest_wire2_{dest_site};

    wire d_lut_to_f7_{dest_site}, f7_to_f8_{dest_site};
    // Force destination LUT into D position with MUXF7_L and MUXF8
    (* KEEP, DONT_TOUCH, LOC = "{dest_site}" *)
    LUT6_L #(
    .INIT(0)
    ) d_lut_rom_{dest_site} (
            .I0(1),
            .I1(1),
            .I2(0),
            .I3(1),
            .I4(1),
            .I5(dest_wire_{dest_site}),
            .LO(d_lut_to_f7_{dest_site})
            );

    wire c_lut_to_f7_{dest_site};
    // Force destination LUT into C position with MUXF7_L and MUXF8
    (* KEEP, DONT_TOUCH, LOC = "{dest_site}" *)
    LUT6_L #(
    .INIT(0)
    ) c_lut_rom_{dest_site} (
            .I0(1),
            .I1(1),
            .I2(0),
            .I3(1),
            .I4(1),
            .I5(dest_wire2_{dest_site}),
            .LO(c_lut_to_f7_{dest_site})
            );
    (* KEEP, DONT_TOUCH, LOC = "{dest_site}" *)
    MUXF7_L f7_{dest_site} (
        .I0(d_lut_to_f7_{dest_site}),
        .I1(c_lut_to_f7_{dest_site}),
        .LO(f7_to_f8_{dest_site})
        );
    (* KEEP, DONT_TOUCH, LOC = "{dest_site}" *)
    MUXF8 f8_{dest_site} (
        .I0(f7_to_f8_{dest_site})
        );

    assign dest_wire_{dest_site} = {dest_wire};
    assign dest_wire2_{dest_site} = {dest_wire2};

    wire dest_wire3_{dest_site2};
    wire dest_wire4_{dest_site2};
    wire lut_to_f7_{dest_site2}, f7_to_f8_{dest_site2};
    // Force destination LUT into D position with MUXF7_L and MUXF8
    (* KEEP, DONT_TOUCH, LOC = "{dest_site2}" *)
    LUT6_L #(
    .INIT(0)
    ) d_lut_rom_{dest_site2} (
            .I0(dest_wire3_{dest_site2}),
            .I1(1),
            .I2(0),
            .I3(1),
            .I4(1),
            .I5(),
            .LO(lut_to_f7_{dest_site2})
            );

    // Force destination LUT into C position with MUXF7_L and MUXF8
    wire c_lut_to_f7_{dest_site2};
    (* KEEP, DONT_TOUCH, LOC = "{dest_site2}" *)
    LUT6_L #(
    .INIT(0)
    ) c_lut_rom_{dest_site2} (
            .I0(dest_wire4_{dest_site2}),
            .I1(1),
            .I2(0),
            .I3(1),
            .I4(1),
            .I5(1),
            .LO(c_lut_to_f7_{dest_site2})
            );
    (* KEEP, DONT_TOUCH, LOC = "{dest_site2}" *)
    MUXF7_L f7_{dest_site2} (
        .I0(lut_to_f7_{dest_site2}),
        .I1(c_lut_to_f7_{dest_site2}),
        .LO(f7_to_f8_{dest_site2})
        );
    (* KEEP, DONT_TOUCH, LOC = "{dest_site2}" *)
    MUXF8 f8_{dest_site2} (
        .I0(f7_to_f8_{dest_site2})
        );

    assign dest_wire3_{dest_site2} = {dest_wire3};
    assign dest_wire4_{dest_site2} = {dest_wire4};
    """.format(
            dest_site=dest_site,
            dest_site2=dest2_site,
            origin_site=origin_site,
            dest_wire=dest_wire,
            dest_wire2=dest_wire2,
            dest_wire3=dest_wire3,
            dest_wire4=dest_wire4,
        ))


def run():
    print('''
module top();
    ''')

    int_tiles = []

    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    params = {}
    for int_l_column, int_r_column in gen_orphan_ints(grid):
        for int_l, int_r in zip(int_l_column[1:6:2], int_r_column[1:6:2]):
            build_cross_int(params, grid, int_l, int_r)
            int_tiles.append(int_l)

    print("endmodule")
    with open('top.txt', 'w') as f:
        for tile in int_tiles:
            print(tile, file=f)


if __name__ == '__main__':
    run()
