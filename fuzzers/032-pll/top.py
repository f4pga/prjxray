import os
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import verilog
from prjxray.verilog import vrandbit, vrandbits
import sys
import json


def gen_sites():
    for _tile_name, site_name, _site_type in sorted(util.get_roi().gen_sites(
        ["PLLE2_ADV"])):
        yield site_name


sites = list(gen_sites())
DUTN = len(sites)
DIN_N = DUTN * 8
DOUT_N = DUTN * 8

verilog.top_harness(DIN_N, DOUT_N)

f = open('params.jl', 'w')
f.write('module,loc,params\n')
print(
    'module roi(input clk, input [%d:0] din, output [%d:0] dout);' %
    (DIN_N - 1, DOUT_N - 1))

for loci, site in enumerate(sites):

    ports = {
        'clk': 'clk',
        'din': 'din[  %d +: 8]' % (8 * loci, ),
        'dout': 'dout[  %d +: 8]' % (8 * loci, ),
    }

    params = {
        "CLKOUT0_DIVIDE": random.randint(1, 128),
    }

    modname = "my_PLLE2_ADV"
    verilog.instance(modname, "inst_%u" % loci, ports, params=params)
    # LOC isn't support
    params["LOC"] = verilog.quote(site)

    j = {'module': modname, 'i': loci, 'params': params}
    f.write('%s\n' % (json.dumps(j)))
    print('')

f.close()
print(
    '''endmodule

// ---------------------------------------------------------------------

''')

print(
    '''
module my_PLLE2_ADV (input clk, input [7:0] din, output [7:0] dout);
    parameter CLKOUT0_DIVIDE = 1;
    parameter CLKOUT1_DIVIDE = 1;
    parameter CLKOUT2_DIVIDE = 1;
    parameter CLKOUT3_DIVIDE = 1;
    parameter CLKOUT4_DIVIDE = 1;
    parameter CLKOUT5_DIVIDE = 1;
    parameter DIVCLK_DIVIDE = 1;
    parameter CLKFBOUT_MULT = 5;

    (* KEEP, DONT_TOUCH *)
    PLLE2_ADV #(
            .CLKOUT0_DIVIDE(CLKOUT0_DIVIDE),
            .CLKOUT1_DIVIDE(CLKOUT1_DIVIDE),
            .CLKOUT2_DIVIDE(CLKOUT2_DIVIDE),
            .CLKOUT3_DIVIDE(CLKOUT3_DIVIDE),
            .CLKOUT4_DIVIDE(CLKOUT4_DIVIDE),
            .CLKOUT5_DIVIDE(CLKOUT5_DIVIDE),
            .DIVCLK_DIVIDE(DIVCLK_DIVIDE),
            .CLKFBOUT_MULT(CLKFBOUT_MULT)
    ) dut(
            .CLKFBOUT(),
            .CLKOUT0(dout[0]),
            .CLKOUT1(),
            .CLKOUT2(),
            .CLKOUT3(),
            .CLKOUT4(),
            .CLKOUT5(),
            .DRDY(),
            .LOCKED(),
            .DO(),
            .CLKFBIN(),
            .CLKIN1(),
            .CLKIN2(),
            .CLKINSEL(),
            .DCLK(),
            .DEN(),
            .DWE(),
            .PWRDWN(),
            .RST(din[0]),
            .DI(),
            .DADDR());
endmodule
''')
