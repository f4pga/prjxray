#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

import os
import json
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util


def gen_sites():
    for tile_name, site_name, _site_type in sorted(util.get_roi().gen_sites(
        ['RAMB18E1', 'FIFO18E1'])):
        yield tile_name, site_name


BITS_PER_PARAM = 256
NUM_INITP_PARAMS = 8
NUM_INIT_PARAMS = 0x40
BITS_PER_SITE = BITS_PER_PARAM * (NUM_INITP_PARAMS + NUM_INIT_PARAMS)


def main():
    print("module top();")

    list_of_params = []
    for tile_name, site in gen_sites():
        params = {}
        params['tile'] = tile_name
        params['site'] = site

        p = []
        for initp_idx in range(NUM_INITP_PARAMS):
            param = 'INITP_{:02X}'.format(initp_idx)
            params[param] = random.randint(0, 2**BITS_PER_PARAM - 1)
            p.append(
                ".{param}(256'h{val:x})".format(
                    param=param, val=params[param]))

        for init_idx in range(NUM_INIT_PARAMS):
            param = 'INIT_{:02X}'.format(init_idx)
            params[param] = random.randint(0, 2**BITS_PER_PARAM - 1)
            p.append(
                ".{param}(256'h{val:x})".format(
                    param=param, val=params[param]))

        params['params'] = ','.join(p)

        print(
            """
    (* KEEP, DONT_TOUCH, LOC = "{site}" *)
    RAMB18E1 #(
        .READ_WIDTH_A(1),
        .READ_WIDTH_B(1),
        .RAM_MODE("TDP"),
        {params}
        ) bram_{site} (
        );
        """.format(**params))

        list_of_params.append(params)

    print("endmodule")

    with open('params.json', 'w') as f:
        json.dump(list_of_params, f, indent=2)


if __name__ == "__main__":
    main()
