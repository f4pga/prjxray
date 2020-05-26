#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
'''
Generate a primitive to place at every I/O
Unlike CLB tests, the LFSR for this is inside the ROI, not driving it
'''

import os
import random
import sys
#random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import verilog


def gen_iobs():
    '''
    IOB33S: main IOB of a diff pair
    IOB33M: secondary IOB of a diff pair
    IOB33: not a diff pair. Relatively rare (at least in ROI...2 of them?)
    Focus on IOB33S to start
    '''
    for _tile_name, site_name, site_type in util.get_roi().gen_sites(
            #['IOB33', 'IOB33S', 'IOB33M']):
        ['IOB33S']):
        yield site_name, site_type


def write_pins(ports):
    pinstr = ''
    for site, (name, dir_, cell) in sorted(ports.items(), key=lambda x: x[1]):
        # pinstr += 'set_property -dict "PACKAGE_PIN %s IOSTANDARD LVCMOS33" [get_ports %s]' % (packpin, port)
        pinstr += '%s,%s,%s,%s\n' % (site, name, dir_, cell)
    open('params.csv', 'w').write(pinstr)


def run():
    # All possible values
    iosites = {}
    for site_name, site_type in gen_iobs():
        iosites[site_name] = site_type

    # Assigned in this design
    ports = {}
    DIN_N = 0
    DOUT_N = 0

    def remain_sites():
        return set(iosites.keys()) - set(ports.keys())

    def rand_site():
        '''Get a random, unused site'''
        return random.choice(list(remain_sites()))

    def get_site():
        return next(iter(remain_sites()))

    def assign_i(site, name):
        nonlocal DIN_N

        assert site not in ports
        cell = "di_bufs[%u].ibuf" % DIN_N
        DIN_N += 1
        ports[site] = (name, 'input', cell)

    def assign_o(site, name):
        nonlocal DOUT_N

        assert site not in ports
        cell = "do_bufs[%u].obuf" % DOUT_N
        DOUT_N += 1
        ports[site] = (name, 'output', cell)

    # Assign at least one di and one do
    assign_i(get_site(), 'di[0]')
    assign_o(get_site(), 'do[0]')
    # Now assign the rest randomly
    #while len(remain_sites()):
    #        assign_o(rand_site(), 'do[%u]' % DOUT_N)

    #write_pins(ports)

    print(
        '''
`define N_DI %u
`define N_DO %u

module top(input wire [`N_DI-1:0] di, output wire [`N_DO-1:0] do);
    genvar i;

    //Instantiate BUFs so we can LOC them

    wire [`N_DI-1:0] di_buf;
    generate
        for (i = 0; i < `N_DI; i = i+1) begin:di_bufs
            IBUF #(
            ) ibuf(.I(di[i]), .O(di_buf[i]));
        end
    endgenerate

    wire [`N_DO-1:0] do_unbuf;
    generate
        for (i = 0; i < `N_DO; i = i+1) begin:do_bufs
            OBUF #(
            ) obuf(.I(do_unbuf[i]), .O(do[i]));
        end
    endgenerate

    roi roi(.di(di_buf), .do(do_unbuf));
endmodule

//Arbitrary terminate into LUTs
module roi(input wire [`N_DI-1:0] di, output wire [`N_DO-1:0] do);
    genvar i;

    generate
        for (i = 0; i < `N_DI; i = i+1) begin:dis
            (* KEEP, DONT_TOUCH *)
            LUT6 #(
                    .INIT(64'h8000_0000_0000_0001)
            ) lut (
                    .I0(di[i]),
                    .I1(di[i]),
                    .I2(di[i]),
                    .I3(di[i]),
                    .I4(di[i]),
                    .I5(di[i]),
                    .O());
        end
    endgenerate

    generate
        for (i = 0; i < `N_DO; i = i+1) begin:dos
            (* KEEP, DONT_TOUCH *)
            LUT6 #(
                    .INIT(64'h8000_0000_0000_0001)
            ) lut (
                    .I0(),
                    .I1(),
                    .I2(),
                    .I3(),
                    .I4(),
                    .I5(),
                    .O(do[i]));
        end
    endgenerate
endmodule
    ''' % (DIN_N, DOUT_N))


if __name__ == '__main__':
    run()
