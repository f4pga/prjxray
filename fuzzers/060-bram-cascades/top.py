import os
import sys
import random
import math
from prjxray import util
from prjxray.db import Database
random.seed(int(os.getenv("SEED"), 16))

def bram_count():
    db = Database(util.get_db_root())
    grid = db.grid()

    count = 0
    for tile_name in grid.tiles():
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site_name, site_type in gridinfo.sites.items():
            if site_type in ['RAMBFIFO36E1']:
                count += 1

    return count

class LutMaker(object):
    def __init__(self):
        self.input_lut_idx = 0
        self.output_lut_idx = 0
        self.lut_input_idx = 0

    def get_next_input_net(self):
        net = 'lut_{}_i[{}]'.format(self.input_lut_idx, self.lut_input_idx)

        self.lut_input_idx += 1
        if self.lut_input_idx > 5:
            self.lut_input_idx = 0
            self.input_lut_idx += 1

        return net

    def get_next_output_net(self):
        net = 'lut_{}_o'.format(self.output_lut_idx)
        self.output_lut_idx += 1
        return net

    def create_wires_and_luts(self):
        if self.output_lut_idx > self.input_lut_idx:
            nluts = self.output_lut_idx
        else:
            nluts = self.input_lut_idx
            if self.lut_input_idx > 0:
                nluts += 1

        for lut in range(nluts):
            yield """
            wire [5:0] lut_{lut}_i;
            wire lut_{lut}_o;

            (* KEEP, DONT_TOUCH *)
            LUT6 lut_{lut} (
                .I0(lut_{lut}_i[0]),
                .I1(lut_{lut}_i[1]),
                .I2(lut_{lut}_i[2]),
                .I3(lut_{lut}_i[3]),
                .I4(lut_{lut}_i[4]),
                .I5(lut_{lut}_i[5]),
                .O(lut_{lut}_o)
            );
            """.format(lut=lut)

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

    lines.append('''
    wire [9:0] {name}_wraddr;
    wire [9:0] {name}_rdaddr;
    '''.format(name=name))

    for bit in range(10):
        lines.append("""
    assign {name}_wraddr[{bit}] = {net};""".format(
        name=name,
        bit=bit,
        net=luts.get_next_output_net()))

    for bit in range(10):
        lines.append("""
    assign {name}_rdaddr[{bit}] = {net};""".format(
        name=name,
        bit=bit,
        net=luts.get_next_output_net()))

    lines.append('''
    (* KEEP, DONT_TOUCH *)
    {name} {name}_inst(
        .wraddr({name}_wraddr),
        .rdaddr({name}_rdaddr)
    );
    '''.format(name=name))

    return width, address_bits, math.ceil(float(width)/72)*72*(2**address_bits)

def max_address_bits(width):
    return math.floor(math.log(float(MAX_BRAM*36*1024)/width, 2))

def random_sdp_bram(luts, name, modules, lines):
    sdp_choices = set()

    for width in (1, 18, 36):
        sdp_choices.add((width, (1, max_address_bits(width))))

    for nbram in range(2, MAX_BRAM+1):
        #sdp_choices.add((nbram*32, (1, max_address_bits(nbram*32))))
        #sdp_choices.add((nbram*36, (1, max_address_bits(nbram*36))))
        #sdp_choices.add((nbram*16, (1, max_address_bits(nbram*16))))
        #sdp_choices.add((nbram*32, (1, max_address_bits(nbram*32))))

        # Bias some wide but shallow BRAMs to toggle the lower address bits
        # more.
        for address_bits in range(1, 4):
            sdp_choices.add((nbram*32, (address_bits, address_bits)))

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
        width, address_bits, bits = random_sdp_bram(luts, "ram{}".format(idx), modules, lines)

        brams = math.ceil(bits/float(36*1024))

        count -= brams

        print(width, address_bits, bits, brams, count, file=sys.stderr)
        idx += 1

        if idx >= max_bram_count:
            break

    for module in modules:
        print(module)

    print(
        '''
module top();
''')

    for lut in luts.create_wires_and_luts():
        print(lut)

    for l in lines:
        print(l)

    print("endmodule")


if __name__ == '__main__':
    run()

