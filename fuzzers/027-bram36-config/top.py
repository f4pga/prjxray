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
import os
import random
import json
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import verilog


def gen_bram36():
    for tile_name, site_name, _site_type in util.get_roi().gen_sites(
        ['RAMBFIFO36E1']):
        yield tile_name, site_name


RAM_EXTENSION_OPTS = [
    "NONE",
    "LOWER",
    "UPPER",
]


def main():
    print('''
module top();
    ''')

    params = []
    for tile_name, site_name in gen_bram36():
        ram_extension_a = random.choice(RAM_EXTENSION_OPTS)
        ram_extension_b = random.choice(RAM_EXTENSION_OPTS)
        en_ecc_read = random.randint(0, 1)
        en_ecc_write = random.randint(0, 1)

        print(
            '''
            (* KEEP, DONT_TOUCH, LOC = "{site}" *)
            RAMB36E1 #(
                .READ_WIDTH_A(1),
                .WRITE_WIDTH_A(1),
                .READ_WIDTH_B(1),
                .WRITE_WIDTH_B(1),
                .RAM_EXTENSION_A({ram_extension_a}),
                .RAM_EXTENSION_B({ram_extension_b}),
                .EN_ECC_READ({en_ecc_read}),
                .EN_ECC_WRITE({en_ecc_write})
                ) bram_{site} (
                    .CLKARDCLK(),
                    .CLKBWRCLK(),
                    .ENARDEN(),
                    .ENBWREN(),
                    .REGCEAREGCE(),
                    .REGCEB(),
                    .RSTRAMARSTRAM(),
                    .RSTRAMB(),
                    .RSTREGARSTREG(),
                    .RSTREGB(),
                    .ADDRARDADDR(),
                    .ADDRBWRADDR(),
                    .DIADI(),
                    .DIBDI(),
                    .DIPADIP(),
                    .DIPBDIP(),
                    .WEA(),
                    .WEBWE(),
                    .DOADO(),
                    .DOBDO(),
                    .DOPADOP(),
                    .DOPBDOP());
            '''.format(
                site=site_name,
                ram_extension_a=verilog.quote(ram_extension_a),
                ram_extension_b=verilog.quote(ram_extension_b),
                en_ecc_read=en_ecc_read,
                en_ecc_write=en_ecc_write,
            ))

        params.append(
            {
                'tile': tile_name,
                'site': site_name,
                'RAM_EXTENSION_A': ram_extension_a,
                'RAM_EXTENSION_B': ram_extension_b,
                'EN_ECC_READ': en_ecc_read,
                'EN_ECC_WRITE': en_ecc_write,
            })

    print("endmodule")

    with open('params.json', 'w') as f:
        json.dump(params, f, indent=2)


if __name__ == '__main__':
    main()
