import os
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import verilog
import sys
import json


def gen_bram18():
    # yield "RAMB18_X%dY%d" % (x, y)
    for _tile_name, site_name, _site_type in util.get_roi().gen_sites(
        ['RAMB18E1']):
        yield site_name


def gen_bram36():
    #yield "RAMB36_X%dY%d" % (x, y)
    for _tile_name, site_name, _site_type in util.get_roi().gen_sites(
        ['RAMBFIFO36E1']):
        yield site_name


def gen_brams():
    '''
    Correctly assign a site to either bram36 or 2x bram18
    '''
    # FIXME
    #yield ('RAMBFIFO36E1', "RAMB36_X0Y20")
    #return

    #for _tile_name, site_name, _site_type in util.get_roi().gen_tiles():
    for site in gen_bram36():
        yield ('RAMBFIFO36E1', site)


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


def vrandbit():
    if random.randint(0, 1):
        return "1'b1"
    else:
        return "1'b0"


for loci, (site_type, site) in enumerate(brams):

    def place_bram18():
        assert 0, 'FIXME'

    def place_bram36():
        ports = {
            'clk': 'clk',
            'din': 'din[  %d +: 8]' % (8 * loci, ),
            'dout': 'dout[  %d +: 8]' % (8 * loci, ),
        }
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
            'RAM_MODE': '"TDP"',
            'WRITE_MODE_A': '"WRITE_FIRST"',
            'WRITE_MODE_B': '"WRITE_FIRST"',
        }
        if 0:
            # FIXME
            params = {
                'LOC': verilog.quote(site),
                'IS_CLKARDCLK_INVERTED': "1'b0",
                'IS_CLKBWRCLK_INVERTED': "1'b0",
                #'IS_ENARDEN_INVERTED': vrandbit(),
                'IS_ENARDEN_INVERTED':
                ("1'b" + str(int(os.getenv("SEEDN")) - 1)),
                'IS_ENBWREN_INVERTED': "1'b0",
                'IS_RSTRAMARSTRAM_INVERTED': "1'b0",
                'IS_RSTRAMB_INVERTED': "1'b0",
                'IS_RSTREGARSTREG_INVERTED': "1'b0",
                'IS_RSTREGB_INVERTED': "1'b0",
                'RAM_MODE': '"TDP"',
                'WRITE_MODE_A': '"WRITE_FIRST"',
                'WRITE_MODE_B': '"WRITE_FIRST"',
            }
        return ('my_RAMB36E1', ports, params)

    modname, ports, params = {
        'RAMB18E1': place_bram18,
        'RAMBFIFO36E1': place_bram36,
    }[site_type]()

    verilog.instance(modname, 'inst_%u' % loci, ports, params=params)

    j = {'module': modname, 'i': loci, 'params': params}
    f.write('%s\n' % (json.dumps(j)))
    print('')
'''



def randbits(n):
    return ''.join([random.choice(('0', '1')) for _x in range(n)])


loci = 0


def make(module, gen_locs, pdatan, datan):
    global loci

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


#make('my_RAMB18E1', gen_bram18, 0x08, 0x40)
make('my_RAMB36E1', gen_bram36, 0x10, 0x80)
'''

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

    ''')
print('')
print('''\
    (* LOC=LOC *)
    RAMB36E1 #(''')
for i in range(16):
    print("            .INITP_%02X(256'b0)," % (i, ))
print('')
for i in range(0x80):
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
