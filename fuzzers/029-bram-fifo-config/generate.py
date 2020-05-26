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
    # Filter out interconnect bits.
    if frame in [0, 1, 17, 23, 25]:
        return False

    # ZINV_RSTRAMARSTRAM seems hard to de-correlate from FIFO_Y0_IN_USE.
    if (frame, bit) == (27, 116):
        return False

    return True


def main():
    segmk = Segmaker("design.bits")

    print("Loading tags")
    with open('params.json') as f:
        params = json.load(f)

    for tile_param in params:
        for param, tag in (
            ('Y0_IN_USE', 'RAMB18_Y0.IN_USE'),
            ('Y1_IN_USE', 'RAMB18_Y1.IN_USE'),
            ('FIFO_Y0_IN_USE', 'RAMB18_Y0.FIFO_MODE'),
            ('FIFO_Y1_IN_USE', 'RAMB18_Y1.FIFO_MODE'),
        ):
            segmk.add_tile_tag(tile_param['tile'], tag, tile_param[param])

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


if __name__ == '__main__':
    main()
