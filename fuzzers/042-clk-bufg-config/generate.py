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


#Decouple interconnect bits from PRESELECT property bits
def bitfilter(frame, bit):
    if frame == 7 or frame == 21:
        return False
    return True


def main():
    segmk = Segmaker("design.bits")

    print("Loading tags")
    with open('params.json') as f:
        params = json.load(f)

    for row in params:
        base_name = 'BUFGCTRL_X{}Y{}'.format(row['x'], row['y'])

        segmk.add_site_tag(
            row['site'], '{}.IN_USE'.format(base_name), row['IN_USE'])

        if not row['IN_USE']:
            continue

        for param in (
                'INIT_OUT',
                'IS_IGNORE0_INVERTED',
                'IS_IGNORE1_INVERTED',
        ):
            segmk.add_site_tag(
                row['site'], '{}.{}'.format(base_name, param), row[param])

        for param in ('PRESELECT_I0', ):
            segmk.add_site_tag(
                row['site'], '{}.Z{}'.format(base_name, param), 1 ^ row[param])

        for param in ('PRESELECT_I1', ):
            segmk.add_site_tag(
                row['site'], '{}.{}'.format(base_name, param), row[param])

        for param, tag in (('IS_CE0_INVERTED', 'ZINV_CE0'), ('IS_S0_INVERTED',
                                                             'ZINV_S0'),
                           ('IS_CE1_INVERTED', 'ZINV_CE1'), ('IS_S1_INVERTED',
                                                             'ZINV_S1')):
            segmk.add_site_tag(
                row['site'], '{}.{}'.format(base_name, tag), 1 ^ row[param])

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


if __name__ == '__main__':
    main()
