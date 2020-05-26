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


def main():
    segmk = Segmaker("design.bits")

    print("Loading tags")
    with open('params.json') as f:
        params = json.load(f)

    for row in params:
        base_name = 'BUFHCE_X{}Y{}'.format(row['x'], row['y'])

        segmk.add_site_tag(
            row['site'], '{}.IN_USE'.format(base_name), row['IN_USE'])
        if not row['IN_USE']:
            continue

        segmk.add_site_tag(
            row['site'], '{}.INIT_OUT'.format(base_name), row['INIT_OUT'])

        segmk.add_site_tag(
            row['site'], '{}.ZINV_CE'.format(base_name),
            1 ^ row['IS_CE_INVERTED'])

        # SYNC is a zero pattern
        for opt in ['ASYNC']:
            segmk.add_site_tag(
                row['site'], '{}.CE_TYPE.'.format(base_name) + opt,
                verilog.unquote(row['CE_TYPE']) == opt)

    segmk.compile()
    segmk.write()


if __name__ == '__main__':
    main()
