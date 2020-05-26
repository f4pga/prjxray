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
import sys
import random
import math
from prjxray import util
from prjxray.lut_maker import LutMaker
from prjxray.db import Database
random.seed(int(os.getenv("SEED"), 16))


def bram_count():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    count = 0
    for tile_name in grid.tiles():
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site_name, site_type in gridinfo.sites.items():
            if site_type in ['RAMBFIFO36E1']:
                count += 1

    return count


def sdp_bram(name, width, address_bits):
    depth = 2**address_bits

    return '''
module {name}(
    // Write port
    input wrclk,
    input [{width}-1:0] di,
    input wren,
    input [{address_bits}-1:0] wraddr,
    // Read port
    input rdclk,
    input rden,
    input [{address_bits}-1:0] rdaddr,
    output reg [{width}-1:0] do);

    (* ram_style = "block" *) reg [{width}-1:0] ram[0:{depth}];

    always @ (posedge wrclk) begin
        if(wren == 1) begin
            ram[wraddr] <= di;
        end
    end

    always @ (posedge rdclk) begin
        if(rden == 1) begin
            do <= ram[rdaddr];
        end
    end

endmodule
    '''.format(
        name=name,
        width=width,
        address_bits=address_bits,
        depth=depth,
    )


MAX_BRAM = 8


def emit_sdp_bram(luts, name, modules, lines, width, address_bits):
    modules.append(sdp_bram(name=name, width=width, address_bits=address_bits))

    lines.append(
        '''
    wire [{address_bits}-1:0] {name}_wraddr;
    wire [{address_bits}-1:0] {name}_rdaddr;
    '''.format(
            name=name,
            address_bits=address_bits,
        ))

    for bit in range(address_bits):
        lines.append(
            """
    assign {name}_wraddr[{bit}] = {net};""".format(
                name=name, bit=bit, net=luts.get_next_output_net()))

    for bit in range(address_bits):
        lines.append(
            """
    assign {name}_rdaddr[{bit}] = {net};""".format(
                name=name, bit=bit, net=luts.get_next_output_net()))

    lines.append(
        '''
    (* KEEP, DONT_TOUCH *)
    {name} {name}_inst(
        .wraddr({name}_wraddr),
        .rdaddr({name}_rdaddr)
    );
    '''.format(name=name))

    return width, address_bits, math.ceil(
        float(width) / 72) * 72 * (2**address_bits)


def max_address_bits(width):
    return math.floor(math.log(float(MAX_BRAM * 36 * 1024) / width, 2))


def random_sdp_bram(luts, name, modules, lines):
    sdp_choices = set()

    for width in (1, 2, 4, 8, 16, 18, 32, 36):
        sdp_choices.add((width, (1, max_address_bits(width))))

    for nbram in range(2, MAX_BRAM + 1):
        sdp_choices.add((nbram * 32, (1, max_address_bits(nbram * 32))))
        sdp_choices.add((nbram * 36, (1, max_address_bits(nbram * 36))))
        sdp_choices.add((nbram * 16, (1, max_address_bits(nbram * 16))))
        sdp_choices.add((nbram * 32, (1, max_address_bits(nbram * 32))))

        # Bias some wide but shallow BRAMs to toggle the lower address bits
        # more.
        for address_bits in range(1, 4):
            sdp_choices.add((nbram * 16, (address_bits, address_bits)))

    sdp_choices = sorted(sdp_choices)

    width, address_bits_range = random.choice(sdp_choices)
    address_bits = random.randint(*address_bits_range)
    return emit_sdp_bram(luts, name, modules, lines, width, address_bits)


def run():
    luts = LutMaker()
    count = bram_count()

    max_bram_count = random.randint(1, 200)

    modules = []
    lines = []

    idx = 0
    while count > MAX_BRAM:
        width, address_bits, bits = random_sdp_bram(
            luts, "ram{}".format(idx), modules, lines)

        brams = math.ceil(bits / float(36 * 1024))

        count -= brams

        print(width, address_bits, bits, brams, count, file=sys.stderr)
        idx += 1

        if idx >= max_bram_count:
            break

    for module in modules:
        print(module)

    print('''
module top();
''')

    for lut in luts.create_wires_and_luts():
        print(lut)

    for l in lines:
        print(l)

    print("endmodule")


if __name__ == '__main__':
    run()
