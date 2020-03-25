#!/usr/bin/env python3

from os import environ, getcwd, chdir
import json
from tempfile import TemporaryDirectory
from contextlib import contextmanager
from unittest import TestCase, main

# Setup location of database file to a relative term so it can be generated
# in the current subdirectory, which will be a temporary one, to allow concurent
# testing.
environ['XRAY_DATABASE_ROOT'] = '.'
environ['XRAY_PART'] = './'

from prjxray.util import get_roi


@contextmanager
def setup_database(contents):
    with TemporaryDirectory() as d:
        olddir = getcwd()
        chdir(d)
        e = None
        with open('tilegrid.json', 'w') as fd:
            json.dump(contents, fd)
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


if __name__ == '__main__':
    main()
