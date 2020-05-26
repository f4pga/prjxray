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
from __future__ import print_function
import prjxray.db
import prjxray.util
import argparse


def quick_test(db_root, part):
    db = prjxray.db.Database(db_root, part)
    g = db.grid()

    # Verify that we have some tile information for every tile in grid.
    tile_types_in_grid = set(
        g.gridinfo_at_loc(loc).tile_type for loc in g.tile_locations())
    tile_types_in_db = set(db.get_tile_types())
    site_types = set(db.get_site_types())
    assert len(tile_types_in_grid - tile_types_in_db) == 0

    # Verify that all tile types can be loaded.
    for tile_type in db.get_tile_types():
        tile = db.get_tile_type(tile_type)
        wires = tile.get_wires()
        for site in tile.get_sites():
            assert site.type in site_types
            site_type = db.get_site_type(site.type)
            site_pins = site_type.get_site_pins()
            for site_pin in site.site_pins:
                if site_pin.wire is not None:
                    assert site_pin.wire in wires, (site_pin.wire, )

                assert site_pin.name in site_pins

        for pip in tile.get_pips():
            assert pip.net_to in wires
            assert pip.net_from in wires

    for loc in g.tile_locations():
        gridinfo = g.gridinfo_at_loc(loc)
        assert gridinfo.tile_type in db.get_tile_types()
        for site_name, site_type in gridinfo.sites.items():
            assert site_type in site_types

        tile = db.get_tile_type(gridinfo.tile_type)

        instance_sites = list(tile.get_instance_sites(gridinfo))
        assert len(instance_sites) == len(tile.get_sites())


def main():
    parser = argparse.ArgumentParser(
        description="Runs a sanity check on a prjxray database.")

    util.db_root_arg(parser)
    util.part_arg(parser)

    args = parser.parse_args()

    quick_test(args.db_root, args.part)


if __name__ == '__main__':
    main()
