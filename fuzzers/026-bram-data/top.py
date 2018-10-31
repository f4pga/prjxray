#!/usr/bin/env python

import os
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import verilog
import sys


def gen_bram36():
    #yield "RAMB36_X%dY%d" % (x, y)
    for _tile_name, site_name, _site_type in util.get_roi().gen_sites(
        ['RAMBFIFO36E1']):
        yield site_name


DUTN = 10
DIN_N = DUTN * 8
DOUT_N = DUTN * 8

verilog.top_harness(DIN_N, DOUT_N)

f = open('params.csv', 'w')
f.write('module,loc,pdata,data\n')
print(
    'module roi(input clk, input [%d:0] din, output [%d:0] dout);' %
    (DIN_N - 1, DOUT_N - 1))


def randbits(n):
    return ''.join([random.choice(('0', '1')) for _x in range(n)])


def make(module, gen_locs, pdatan, datan):
    loci = 0

    for loci, loc in enumerate(gen_locs()):
        if loci >= DUTN:
            break

        pdata = randbits(pdatan * 0x100)
        data = randbits(datan * 0x100)

        print('    %s #(' % module)
        for i in range(pdatan):
            print(
                "        .INITP_%02X(256'b%s)," %
                (i, pdata[i * 256:(i + 1) * 256]))
        for i in range(datan):
            print(
                "        .INIT_%02X(256'b%s)," %
                (i, data[i * 256:(i + 1) * 256]))
        print('        .LOC("%s"))' % (loc, ))
        print(
            '            inst_%d (.clk(clk), .din(din[  %d +: 8]), .dout(dout[  %d +: 8]));'
            % (loci, 8 * loci, 8 * loci))

        f.write('%s,%s,%s,%s\n' % (module, loc, pdata, data))
        print('')
        loci += 1
    assert loci == DUTN


make('my_RAMB36E1', gen_bram36, 0x10, 0x80)

f.close()
print(
    '''endmodule

// ---------------------------------------------------------------------

''')

print(
    '''
module my_RAMB36E1 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    ''')
for i in range(16):
    print(
        "    parameter INITP_%02X = 256'h0000000000000000000000000000000000000000000000000000000000000000;"
        % i)
print('')
for i in range(0x80):
    print(
        "    parameter INIT_%02X = 256'h0000000000000000000000000000000000000000000000000000000000000000;"
        % i)
print('')
print('''\
    (* LOC=LOC *)
    RAMB36E1 #(''')
for i in range(16):
    print('            .INITP_%02X(INITP_%02X),' % (i, i))
print('')
for i in range(0x80):
    print('            .INIT_%02X(INIT_%02X),' % (i, i))
print('')
print(
    '''
            .IS_CLKARDCLK_INVERTED(1'b0),
            .IS_CLKBWRCLK_INVERTED(1'b0),
            .IS_ENARDEN_INVERTED(1'b0),
            .IS_ENBWREN_INVERTED(1'b0),
            .IS_RSTRAMARSTRAM_INVERTED(1'b0),
            .IS_RSTRAMB_INVERTED(1'b0),
            .IS_RSTREGARSTREG_INVERTED(1'b0),
            .IS_RSTREGB_INVERTED(1'b0),
            .RAM_MODE("TDP"),
            .WRITE_MODE_A("WRITE_FIRST"),
            .WRITE_MODE_B("WRITE_FIRST"),
            .SIM_DEVICE("VIRTEX6")
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
            .WEA(din[0]),
            .WEBWE(din[1]),
            .DOADO(dout[0]),
            .DOBDO(dout[1]),
            .DOPADOP(dout[2]),
            .DOPBDOP(dout[3]));
endmodule
''')
