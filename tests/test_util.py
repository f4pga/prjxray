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

from os import environ, getcwd, chdir, mkdir, environ
import json
from tempfile import TemporaryDirectory
from contextlib import contextmanager
from unittest import TestCase, main

# Setup location of database file to a relative term so it can be generated
# in the current subdirectory, which will be a temporary one, to allow concurent
# testing.
environ['XRAY_DATABASE_ROOT'] = '.'
environ['XRAY_PART'] = 'xc7a200tffg1156-1'

from prjxray.util import get_roi, get_db_root
from prjxray.overlay import Overlay
from prjxray.grid_types import GridLoc


@contextmanager
def setup_database(contents):
    with TemporaryDirectory() as d:
        olddir = getcwd()
        chdir(d)
        mkdir('xc7a200t')
        mkdir('mapping')
        environ['XRAY_DATABASE_ROOT'] = d
        e = None
        with open('xc7a200t/tilegrid.json', 'w') as fd:
            json.dump(contents, fd)
        # Create some dummy data
        with open('mapping/devices.yaml', 'w') as fd:
            json.dump({'xc7a200t': {'fabric': "xc7a200t"}}, fd)
        with open('mapping/parts.yaml', 'w') as fd:
            json.dump({'xc7a200tffg1156-1': {"device": "xc7a200t"}}, fd)

        try:
            yield
        except Exception as ereal:
            e = ereal
        chdir(olddir)
        if e is not None:
            raise e


class TestUtil(TestCase):
    def test_get_roi_gen_sites(self):
        makedb = lambda sites: {
                "ATILE": {
                    "bits": {
                        "CLB_IO_CLK": {
                            "baseaddr": "0x00400F00",
                            "frames": 28,
                            "height": 2,
                            "offset": 0,
                            "words": 2
                        }
                    },
                    "grid_x": 10,
                    "grid_y": 10,
                    "segment": "ASEGMENT",
                    "segment_type": "bram0_l",
                    "sites": sites,
                    "prohibited_sites": [],
                    "type": "BRAM_INT_INTERFACE_L"
                }
            }
        with setup_database(makedb({})):
            self.assertListEqual(list(get_roi().gen_sites()), [])
        with setup_database(makedb({'FOO': 'BAR'})):
            self.assertListEqual(
                list(get_roi().gen_sites()), [('ATILE', 'FOO', 'BAR')])

    def test_in_roi_overlay(self):
        region_dict = {}
        region_dict['pr1'] = (10, 58, 0, 51)
        region_dict['pr2'] = (10, 58, 52, 103)
        overlay = Overlay(region_dict)
        self.assertFalse(overlay.tile_in_roi(GridLoc(18, 50)))
        self.assertFalse(overlay.tile_in_roi(GridLoc(18, 84)))
        self.assertTrue(overlay.tile_in_roi(GridLoc(8, 50)))
        self.assertTrue(overlay.tile_in_roi(GridLoc(18, 112)))
        self.assertTrue(overlay.tile_in_roi(GridLoc(80, 40)))


if __name__ == '__main__':
    main()
