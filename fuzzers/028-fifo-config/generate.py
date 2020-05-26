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
from prjxray import verilog


def add_enum_bits(segmk, params, key, options):
    for opt in options:
        segmk.add_site_tag(
            params['tile'], '{}_{}'.format(key, opt), params[key] == opt)


def output_integer_tags(segmk, params, key, invert=False):
    tile = params['tile']
    bits = verilog.parse_bitstr(params[key])
    for bit, tag_val in enumerate(bits):
        if not invert:
            segmk.add_tile_tag(
                tile, "{}[{}]".format(key,
                                      len(bits) - bit - 1), tag_val)
        else:
            segmk.add_tile_tag(
                tile, "Z{}[{}]".format(key,
                                       len(bits) - bit - 1),
                0 if tag_val else 1)


def main():
    segmk = Segmaker("design.bits")

    print("Loading tags")
    with open('params.json') as f:
        params = json.load(f)

    for tile_param in params:
        if tile_param['EN_SYN'] and tile_param['DATA_WIDTH'] == 4:
            output_integer_tags(
                segmk, tile_param, 'ALMOST_EMPTY_OFFSET', invert=True)
            output_integer_tags(
                segmk, tile_param, 'ALMOST_FULL_OFFSET', invert=True)

        for param in ('EN_SYN', 'FIRST_WORD_FALL_THROUGH'):
            segmk.add_tile_tag(tile_param['tile'], param, tile_param[param])

    segmk.compile()
    segmk.write()


if __name__ == '__main__':
    main()
