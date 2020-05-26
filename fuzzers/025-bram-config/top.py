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
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import verilog
from prjxray.verilog import vrandbit, vrandbits
import json


def gen_bram18():
    '''
    sample:
    "sites": {
        "RAMB18_X0Y50": "FIFO18E1",
        "RAMB18_X0Y51": "RAMB18E1",
        "RAMB36_X0Y25": "RAMBFIFO36E1"
    },
    '''
    for _tile_name, site_name, _site_type in sorted(util.get_roi().gen_sites(
        ['RAMB18E1', 'FIFO18E1'])):
        yield site_name


def gen_bram36():
    for _tile_name, site_name, _site_type in util.get_roi().gen_sites(
        ['RAMBFIFO36E1']):
        yield site_name


def gen_brams():
    '''
    Correctly assign a site to either bram36 or 2x bram18
    '''
    # XXX: mix 18 and 36?
    for site in gen_bram18():
        yield ('RAMB18E1', site)


def place_bram18(site, loci):
    ports = {
        'clk': 'clk',
        'din': 'din[  %d +: 8]' % (8 * loci, ),
        'dout': 'dout[  %d +: 8]' % (8 * loci, ),
    }

    write_modes = ["WRITE_FIRST", "READ_FIRST", "NO_CHANGE"]
    collisions = ["DELAYED_WRITE", "PERFORMANCE"]
    priorities = ["RSTREG", "REGCE"]

    # Datasheet says 72 is legal in some cases, but think its a copy paste error from BRAM36
    # also 0 and 36 aren't real sizes
    # Bias choice to 18 as its needed to solve certain bits quickly
    widths = [1, 2, 4, 9, 18, 18, 36]
    mode = '"TDP"'

    read_width_a = random.choice(widths)
    write_width_b = random.choice(widths)
    if read_width_a >= 36 or write_width_b >= 36:
        read_width_b = 0
        write_width_a = 0
        mode = '"SDP"'
        doa_reg = vrandbit()
        dob_reg = doa_reg
        write_modes = ["WRITE_FIRST", "READ_FIRST"]
        rstreg_priority_a = verilog.quote(random.choice(priorities))
        rstreg_priority_b = rstreg_priority_a
    else:
        read_width_b = random.choice(widths)
        write_width_a = random.choice(widths)
        doa_reg = vrandbit()
        dob_reg = vrandbit()
        rstreg_priority_a = verilog.quote(random.choice(priorities))
        rstreg_priority_b = verilog.quote(random.choice(priorities))

    params = {
        'LOC': verilog.quote(site),
        'IS_CLKARDCLK_INVERTED': vrandbit(),
        'IS_CLKBWRCLK_INVERTED': vrandbit(),
        'IS_ENARDEN_INVERTED': vrandbit(),
        'IS_ENBWREN_INVERTED': vrandbit(),
        'IS_RSTRAMARSTRAM_INVERTED': vrandbit(),
        'IS_RSTRAMB_INVERTED': vrandbit(),
        'IS_RSTREGARSTREG_INVERTED': vrandbit(),
        'IS_RSTREGB_INVERTED': vrandbit(),
        'RAM_MODE': mode,
        'WRITE_MODE_A': verilog.quote(random.choice(write_modes)),
        'WRITE_MODE_B': verilog.quote(random.choice(write_modes)),
        "DOA_REG": doa_reg,
        "DOB_REG": dob_reg,
        "SRVAL_A": vrandbits(18),
        "SRVAL_B": vrandbits(18),
        "INIT_A": vrandbits(18),
        "INIT_B": vrandbits(18),
        "READ_WIDTH_A": read_width_a,
        "READ_WIDTH_B": read_width_b,
        "WRITE_WIDTH_A": write_width_a,
        "WRITE_WIDTH_B": write_width_b,
        "RDADDR_COLLISION_HWCONFIG": verilog.quote(random.choice(collisions)),
        "RSTREG_PRIORITY_A": rstreg_priority_a,
        "RSTREG_PRIORITY_B": rstreg_priority_b,
    }

    return ('my_RAMB18E1', ports, params)


def main():
    brams = list(gen_brams())
    DUTN = len(brams)
    DIN_N = DUTN * 8
    DOUT_N = DUTN * 8

    verilog.top_harness(DIN_N, DOUT_N)

    f = open('params.jl', 'w')
    f.write('module,loc,params\n')
    print(
        'module roi(input clk, input [%d:0] din, output [%d:0] dout);' %
        (DIN_N - 1, DOUT_N - 1))

    for loci, (site_type, site) in enumerate(brams):
        modname, ports, params = {
            'RAMB18E1': place_bram18,
            #'RAMBFIFO36E1': place_bram36,
        }[site_type](site, loci)

        verilog.instance(modname, 'inst_%u' % loci, ports, params=params)

        j = {'module': modname, 'i': loci, 'params': params}
        f.write('%s\n' % (json.dumps(j)))
        print('')

    f.close()
    print(
        '''endmodule

    // ---------------------------------------------------------------------

    ''')

    # RAMB18E1
    print(
        '''
    module my_RAMB18E1 (input clk, input [7:0] din, output [7:0] dout);
        parameter LOC = "";
        parameter IS_CLKARDCLK_INVERTED = 1'b0;
        parameter IS_CLKBWRCLK_INVERTED = 1'b0;
        parameter IS_ENARDEN_INVERTED = 1'b0;
        parameter IS_ENBWREN_INVERTED = 1'b0;
        parameter IS_RSTRAMARSTRAM_INVERTED = 1'b0;
        parameter IS_RSTRAMB_INVERTED = 1'b0;
        parameter IS_RSTREGARSTREG_INVERTED = 1'b0;
        parameter IS_RSTREGB_INVERTED = 1'b0;
        parameter RAM_MODE = "TDP";
        parameter WRITE_MODE_A = "WRITE_FIRST";
        parameter WRITE_MODE_B = "WRITE_FIRST";
        parameter RDADDR_COLLISION_HWCONFIG = "DELAYED_WRITE";
        parameter RSTREG_PRIORITY_A = "RSTREG";
        parameter RSTREG_PRIORITY_B = "RSTREG";

        parameter DOA_REG = 1'b0;
        parameter DOB_REG = 1'b0;
        parameter SRVAL_A = 18'b0;
        parameter SRVAL_B = 18'b0;
        parameter INIT_A = 18'b0;
        parameter INIT_B = 18'b0;

        parameter READ_WIDTH_A = 0;
        parameter READ_WIDTH_B = 0;
        parameter WRITE_WIDTH_A = 0;
        parameter WRITE_WIDTH_B = 0;
        ''')
    print('''\
        (* LOC=LOC *)
        RAMB18E1 #(''')
    for i in range(8):
        print("            .INITP_%02X(256'b0)," % (i, ))
    print('')
    for i in range(0x40):
        print("            .INIT_%02X(256'b0)," % (i, ))
    print('')
    print(
        '''
                .IS_CLKARDCLK_INVERTED(IS_CLKARDCLK_INVERTED),
                .IS_CLKBWRCLK_INVERTED(IS_CLKBWRCLK_INVERTED),
                .IS_ENARDEN_INVERTED(IS_ENARDEN_INVERTED),
                .IS_ENBWREN_INVERTED(IS_ENBWREN_INVERTED),
                .IS_RSTRAMARSTRAM_INVERTED(IS_RSTRAMARSTRAM_INVERTED),
                .IS_RSTRAMB_INVERTED(IS_RSTRAMB_INVERTED),
                .IS_RSTREGARSTREG_INVERTED(IS_RSTREGARSTREG_INVERTED),
                .IS_RSTREGB_INVERTED(IS_RSTREGB_INVERTED),
                .RAM_MODE(RAM_MODE),
                .WRITE_MODE_A(WRITE_MODE_A),
                .WRITE_MODE_B(WRITE_MODE_B),

                .DOA_REG(DOA_REG),
                .DOB_REG(DOB_REG),
                .SRVAL_A(SRVAL_A),
                .SRVAL_B(SRVAL_B),
                .INIT_A(INIT_A),
                .INIT_B(INIT_B),

                .READ_WIDTH_A(READ_WIDTH_A),
                .READ_WIDTH_B(READ_WIDTH_B),
                .WRITE_WIDTH_A(WRITE_WIDTH_A),
                .WRITE_WIDTH_B(WRITE_WIDTH_B),

                .RDADDR_COLLISION_HWCONFIG(RDADDR_COLLISION_HWCONFIG),

                .RSTREG_PRIORITY_A(RSTREG_PRIORITY_A),
                .RSTREG_PRIORITY_B(RSTREG_PRIORITY_B)
            ) ram (
                .CLKARDCLK(din[0]),
                .CLKBWRCLK(din[1]),
                .ENARDEN(din[2]),
                .ENBWREN(din[3]),
                .REGCEAREGCE(din[4]),
                .REGCEB(din[5]),
                .RSTRAMARSTRAM(din[6]),
                .RSTRAMB(din[7]),
                .RSTREGARSTREG(din[0]),
                .RSTREGB(din[1]),
                .ADDRARDADDR(din[2]),
                .ADDRBWRADDR(din[3]),
                .DIADI(din[4]),
                .DIBDI(din[5]),
                .DIPADIP(din[6]),
                .DIPBDIP(din[7]),
                .WEA(1'b0),
                .WEBWE(din[1]),
                .DOADO(dout[0]),
                .DOBDO(dout[1]),
                .DOPADOP(dout[2]),
                .DOPBDOP(dout[3]));
    endmodule
    ''')


if __name__ == "__main__":
    main()
