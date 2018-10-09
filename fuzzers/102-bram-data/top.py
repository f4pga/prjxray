'''
Need coverage for the following:
RAM32X1S_N
RAM32X1D
RAM32M
RAM64X1S_N
RAM64X1D_N
RAM64M
RAM128X1S_N
RAM128X1D
RAM256X1S
SRL16E_N
SRLC32E_N

Note: LUT6 was added to try to simplify reduction, although it might not be needed
'''

import random
random.seed(0)
import os
import re


def slice_xy():
    '''Return (X1, X2), (Y1, Y2) from XRAY_ROI, exclusive end (for range)'''
    # SLICE_X12Y100:SLICE_X27Y149
    # Note XRAY_ROI_GRID_* is something else
    m = re.match(r'SLICE_X(.*)Y(.*):SLICE_X(.*)Y(.*)', os.getenv('XRAY_ROI'))
    ms = [int(m.group(i + 1)) for i in range(4)]
    return ((ms[0], ms[2] + 1), (ms[1], ms[3] + 1))


# 18 + 36 count in ROI
DUTN = 10
SLICEX, SLICEY = slice_xy()
# 800
SLICEN = (SLICEY[1] - SLICEY[0]) * (SLICEX[1] - SLICEX[0])
print('//SLICEX: %s' % str(SLICEX))
print('//SLICEY: %s' % str(SLICEY))
print('//SLICEN: %s' % str(SLICEN))
print('//Requested DUTs: %s' % str(DUTN))


def gen_bram18():
    # TODO: generate this from DB
    assert ((6, 28) == SLICEX)
    x = 0
    for y in range(40, 60):
        # caller may reject position if needs more room
        yield "RAMB18_X%dY%d" % (x, y)


def gen_bram36():
    # TODO: generate this from DB
    assert ((6, 28) == SLICEX)
    x = 0
    for y in range(20, 29):
        # caller may reject position if needs more room
        yield "RAMB36_X%dY%d" % (x, y)


DIN_N = DUTN * 8
DOUT_N = DUTN * 8

print(
    '''
module top(input clk, stb, di, output do);
    localparam integer DIN_N = %d;
    localparam integer DOUT_N = %d;

    reg [DIN_N-1:0] din;
    wire [DOUT_N-1:0] dout;

    reg [DIN_N-1:0] din_shr;
    reg [DOUT_N-1:0] dout_shr;

    always @(posedge clk) begin
        din_shr <= {din_shr, di};
        dout_shr <= {dout_shr, din_shr[DIN_N-1]};
        if (stb) begin
            din <= din_shr;
            dout_shr <= dout;
        end
    end

    assign do = dout_shr[DOUT_N-1];

    roi roi (
        .clk(clk),
        .din(din),
        .dout(dout)
    );
endmodule
''' % (DIN_N, DOUT_N))

f = open('params.csv', 'w')
f.write('module,loc,pdata,data\n')
print(
    'module roi(input clk, input [%d:0] din, output [%d:0] dout);' %
    (DIN_N - 1, DOUT_N - 1))


def randbits(n):
    return ''.join([random.choice(('0', '1')) for _x in range(n)])


loci = 0


def make(module, gen_locs, pdatan, datan):
    global loci

    for loc in gen_locs():
        pdata = randbits(pdatan * 0x100)
        data = randbits(datan * 0x100)

        print('    %s #(' % module)
        for i in range(pdatan):
            print(
                "    .INITP_%02X(256'b%s)," %
                (i, pdata[i * 256:(i + 1) * 256]))
        for i in range(datan):
            print(
                "    .INIT_%02X(256'b%s)," % (i, data[i * 256:(i + 1) * 256]))
        print('.LOC("%s"))' % (loc, ))
        print(
            '            inst_%d (.clk(clk), .din(din[  %d +: 8]), .dout(dout[  %d +: 8]));'
            % (loci, 8 * loci, 8 * loci))

        f.write('%s,%s,%s,%s\n' % (module, loc, pdata, data))
        loci += 1


#make('my_RAMB18E1', gen_bram18, 0x08, 0x40)
make('my_RAMB36E1', gen_bram36, 0x10, 0x80)

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
    ''')
for i in range(8):
    print(
        "    parameter INITP_%02X = 256'h0000000000000000000000000000000000000000000000000000000000000000;"
        % i)
print()
for i in range(0x40):
    print(
        "    parameter INIT_%02X = 256'h0000000000000000000000000000000000000000000000000000000000000000;"
        % i)
print()
print('''\
    (* LOC=LOC *)
    RAMB18E1 #(''')
for i in range(8):
    print('            .INITP_%02X(INITP_%02X),' % (i, i))
print()
for i in range(0x40):
    print('            .INIT_%02X(INIT_%02X),' % (i, i))
print()
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

print(
    '''

module my_RAMB36E1 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    ''')
for i in range(16):
    print(
        "    parameter INITP_%02X = 256'h0000000000000000000000000000000000000000000000000000000000000000;"
        % i)
print()
for i in range(0x80):
    print(
        "    parameter INIT_%02X = 256'h0000000000000000000000000000000000000000000000000000000000000000;"
        % i)
print()
print('''\
    (* LOC=LOC *)
    RAMB36E1 #(''')
for i in range(16):
    print('            .INITP_%02X(INITP_%02X),' % (i, i))
print()
for i in range(0x80):
    print('            .INIT_%02X(INIT_%02X),' % (i, i))
print()
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
