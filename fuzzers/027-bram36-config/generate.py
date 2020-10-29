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

import json

from prjxray.segmaker import Segmaker


def write_ram_ext_tags(segmk, tile_param):
    for param in ["RAM_EXTENSION_A", "RAM_EXTENSION_B"]:
        set_val = tile_param[param]
        for opt in ["LOWER"]:
            segmk.add_site_tag(
                tile_param['site'], "{}_{}".format(param, opt), set_val == opt)
        segmk.add_site_tag(
            tile_param['site'], "{}_NONE_OR_UPPER".format(param),
            set_val != "LOWER")


def main():
    segmk = Segmaker("design.bits")

    print("Loading tags")
    with open('params.json') as f:
        params = json.load(f)

    for tile_param in params:
        if tile_param['BRAM36_IN_USE']:
            write_ram_ext_tags(segmk, tile_param)

            segmk.add_site_tag(
                tile_param['site'], 'EN_ECC_READ', tile_param['EN_ECC_READ'])
            segmk.add_site_tag(
                tile_param['site'], 'EN_ECC_WRITE', tile_param['EN_ECC_WRITE'])

    for ab in 'ab':
        for rw in 'rw':
            if rw == 'r':
                dir = 'READ'
            else:
                dir = 'WRITE'

            width = tile_param['bram36_{}{}_width'.format(rw, ab)]
            tag = 'BRAM36_{}_WIDTH_{}_1'.format(dir, ab.upper())
            if width == 1:
                segmk.add_site_tag(
                    tile_param['site'], tag, tile_param['BRAM36_IN_USE'])

    segmk.compile()
    segmk.write()


if __name__ == '__main__':
    main()
