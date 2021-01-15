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
from params import boolean_params, hex_params, int_params


def bitfilter(frame, bit):
    # Filter out interconnect bits.
    if frame not in [28, 29]:
        return False

    return True


def main():
    segmk = Segmaker("design.bits")

    print("Loading tags")
    with open('params.json') as f:
        params = json.load(f)

        site = params['site']

        for param, _ in boolean_params:
            value = params[param]

            segmk.add_site_tag(site, param, value)

        for param, digits in hex_params + int_params:
            value = int(params[param])
            bitstr = [
                int(x) for x in "{value:0{digits}b}".format(
                    value=value, digits=digits)[::-1]
            ]

            for i in range(digits):
                segmk.add_site_tag(site, '%s[%u]' % (param, i), bitstr[i])

    segmk.compile(bitfilter=bitfilter)
    segmk.write()


if __name__ == '__main__':
    main()
