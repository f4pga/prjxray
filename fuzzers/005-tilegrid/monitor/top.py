import os
import random
random.seed(int(os.getenv("SEED"), 16))
from prjxray import util
from prjxray import verilog


def gen_sites():
    # yield ("MONITOR_BOT_X46Y79", "XADC_X0Y0")
    for tile_name, site_name, _site_type in util.get_roi().gen_sites(['XADC']):
        yield tile_name, site_name


def write_params(params):
    pinstr = 'tile,val,site\n'
    for tile, (site, val) in sorted(params.items()):
        pinstr += '%s,%s,%s\n' % (tile, val, site)
    open('params.csv', 'w').write(pinstr)


def run():
    print(
        '''
module top(input clk, stb, di, output do);
    localparam integer DIN_N = 8;
    localparam integer DOUT_N = 8;

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
    ''')

    params = {}
    # only one for now, worry about later
    sites = list(gen_sites())
    assert len(sites) == 1, len(sites)
    for (tile_name, site_name), isone in zip(sites,
                                             util.gen_fuzz_states(len(sites))):
        INIT_43 = isone
        params[tile_name] = (site_name, INIT_43)

        print(
            '''
    (* KEEP, DONT_TOUCH *)
    XADC #(/*.LOC("%s"),*/ .INIT_43(%u)) dut_%s(
            .BUSY(),
            .DRDY(),
            .EOC(),
            .EOS(),
            .JTAGBUSY(),
            .JTAGLOCKED(),
            .JTAGMODIFIED(),
            .OT(),
            .DO(),
            .ALM(),
            .CHANNEL(),
            .MUXADDR(),
            .CONVST(),
            .CONVSTCLK(clk),
            .DCLK(clk),
            .DEN(),
            .DWE(),
            .RESET(),
            .VN(),
            .VP(),
            .DI(),
            .VAUXN(),
            .VAUXP(),
            .DADDR());
''' % (site_name, INIT_43, site_name))

    print("endmodule")
    write_params(params)


if __name__ == '__main__':
    run()
