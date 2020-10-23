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
from prjxray.db import Database
from prjxray import util
from prjxray import verilog


def gen_bram36(grid):
    for tile_name in grid.tiles():
        loc = grid.loc_of_tilename(tile_name)

        gridinfo = grid.gridinfo_at_loc(loc)

        found = False
        for site_name, site_type in gridinfo.sites.items():
            if site_type == 'RAMBFIFO36E1':
                found = True
                break

        if found:
            bram36_site_name = site_name
            for site_name, site_type in gridinfo.sites.items():
                if site_type == 'RAMB18E1':
                    bram18_site_name = site_name

                if site_type == 'FIFO18E1':
                    fifo18_site_name = site_name

            yield tile_name, bram36_site_name, bram18_site_name, fifo18_site_name


RAM_EXTENSION_OPTS = [
    "NONE",
    "LOWER",
    "UPPER",
]


def main():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    print('''
module top();
    ''')

    params = []
    for tile_name, bram36_site_name, bram18_site_name, fifo18_site_name in gen_bram36(
            grid):
        if random.random() < .8:
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
                    site=bram36_site_name,
                    ram_extension_a=verilog.quote(ram_extension_a),
                    ram_extension_b=verilog.quote(ram_extension_b),
                    en_ecc_read=en_ecc_read,
                    en_ecc_write=en_ecc_write,
                ))

            params.append(
                {
                    'tile': tile_name,
                    'BRAM36_IN_USE': True,
                    'site': bram36_site_name,
                    'RAM_EXTENSION_A': ram_extension_a,
                    'RAM_EXTENSION_B': ram_extension_b,
                    'EN_ECC_READ': en_ecc_read,
                    'EN_ECC_WRITE': en_ecc_write,
                })
        else:
            print(
                '''
                (* KEEP, DONT_TOUCH, LOC = "{bram18}" *)
                RAMB18E1 #(
                    .READ_WIDTH_A(1),
                    .WRITE_WIDTH_A(1),
                    .READ_WIDTH_B(1),
                    .WRITE_WIDTH_B(1)
                    ) bram_{bram18} (
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

                (* KEEP, DONT_TOUCH, LOC = "{fifo18}" *)
                RAMB18E1 #(
                    .READ_WIDTH_A(1),
                    .WRITE_WIDTH_A(1),
                    .READ_WIDTH_B(1),
                    .WRITE_WIDTH_B(1)
                    ) bram_{fifo18} (
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
                    bram18=bram18_site_name,
                    fifo18=fifo18_site_name,
                ))

            params.append(
                {
                    'tile': tile_name,
                    'BRAM36_IN_USE': False,
                    'site': bram36_site_name,
                })

    print("endmodule")

    with open('params.json', 'w') as f:
        json.dump(params, f, indent=2)


if __name__ == '__main__':
    main()
