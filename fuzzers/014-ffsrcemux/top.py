import random
random.seed(0)
import os
import re
from prjxray import util

CLBN = 600
print('//Requested CLBs: %s' % str(CLBN))


def gen_slices():
    for _tile_name, site_name, _site_type in util.get_roi().gen_sites(
        ['SLICEL', 'SLICEM']):
        yield site_name


DIN_N = CLBN * 4
DOUT_N = CLBN * 1
ffprims = ('FDRE', )
ff_bels = (
    'AFF',
    'A5FF',
    'BFF',
    'B5FF',
    'CFF',
    'C5FF',
    'DFF',
    'D5FF',
)

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
f.write('name,loc,ce,r\n')
slices = gen_slices()
print(
    'module roi(input clk, input [%d:0] din, output [%d:0] dout);' %
    (DIN_N - 1, DOUT_N - 1))
for i in range(CLBN):
    ffprim = random.choice(ffprims)
    force_ce = random.randint(0, 1)
    force_r = random.randint(0, 1)
    # clb_FD clb_FD (.clk(clk), .din(din[  0 +: 4]), .dout(dout[  0]));
    # clb_FD_1 clb_FD_1 (.clk(clk), .din(din[  4 +: 4]), .dout(dout[  1]));
    loc = next(slices)
    #bel = random.choice(ff_bels)
    bel = "AFF"
    name = 'clb_%s' % ffprim
    print('    %s' % name)
    print(
        '            #(.LOC("%s"), .BEL("%s"), .FORCE_CE1(%d), .nFORCE_R0(%d))'
        % (loc, bel, force_ce, force_r))
    print(
        '            clb_%d (.clk(clk), .din(din[  %d +: 4]), .dout(dout[  %d]));'
        % (i, 4 * i, 1 * i))
    f.write('%s,%s,%s,%s\n' % (name, loc, force_ce, force_r))
f.close()
print(
    '''endmodule

// ---------------------------------------------------------------------

''')

print(
    '''
module clb_FDRE (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y114";
    parameter BEL="AFF";
    parameter FORCE_CE1=0;
    parameter nFORCE_R0=1;
    (* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
    FDRE ff (
        .C(clk),
        .Q(dout),
        .CE(din[0] | FORCE_CE1),
        .R(din[1] & nFORCE_R0),
        .D(din[2])
    );
    endmodule
''')
