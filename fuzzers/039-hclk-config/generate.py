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


def bitfilter(frame, bit):
    return True


def main():
    segmk = Segmaker("design.bits")

    print("Loading tags")
    with open('params.json') as f:
        params = json.load(f)

    for row in params:
        base_name = 'BUFR_Y{}'.format(row['y'])

        segmk.add_tile_tag(
            row['tile'], '{}.IN_USE'.format(base_name), row['IN_USE'])

        if not row['IN_USE']:
            continue

        segmk.add_tile_tag(
            row['tile'], '{}.BUFR_DIVIDE.BYPASS'.format(base_name),
            '"BYPASS"' == row['BUFR_DIVIDE'])
        for opt in range(1, 9):
            if row['BUFR_DIVIDE'] == str(opt):
                segmk.add_tile_tag(
                    row['tile'], '{}.BUFR_DIVIDE.D{}'.format(base_name, opt),
                    1)
            elif '"BYPASS"' == row['BUFR_DIVIDE']:
                segmk.add_tile_tag(
                    row['tile'], '{}.BUFR_DIVIDE.D{}'.format(base_name, opt),
                    0)

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


if __name__ == '__main__':
    main()
