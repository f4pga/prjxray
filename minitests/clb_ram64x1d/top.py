import random
random.seed(0)
import os
import re

def slice_xy():
    '''Return (X1, X2), (Y1, Y2) from XRAY_ROI, exclusive end (for xrange)'''
    # SLICE_X12Y100:SLICE_X27Y149
    # Note XRAY_ROI_GRID_* is something else
    m = re.match(r'SLICE_X(.*)Y(.*):SLICE_X(.*)Y(.*)', os.getenv('XRAY_ROI'))
    ms = [int(m.group(i + 1)) for i in range(4)]
    return ((ms[0], ms[2] + 1), (ms[1], ms[3] + 1))

CLBN = 400
SLICEX, SLICEY = slice_xy()
# 800
SLICEN = (SLICEY[1] - SLICEY[0]) * (SLICEX[1] - SLICEX[0])
print('//SLICEX: %s' % str(SLICEX))
print('//SLICEY: %s' % str(SLICEY))
print('//SLICEN: %s' % str(SLICEN))
print('//Requested CLBs: %s' % str(CLBN))

# Rearranged to sweep Y so that carry logic is easy to allocate
# XXX: careful...if odd number of Y in ROI will break carry
def gen_slicems():
    '''
    SLICEM at the following:
    SLICE_XxY*
    Where Y any value
    x
        Always even (ie 100, 102, 104, etc)
        In our ROI
        x = 6, 8, 10, 12, 14
    '''
    # TODO: generate this from DB
    assert((12, 28) == SLICEX)
    for slicex in (6, 8, 10, 12, 14):
        for slicey in range(*SLICEY):
            # caller may reject position if needs more room
            yield ("SLICE_X%dY%d" % (slicex, slicey), (slicex, slicey))

DIN_N = CLBN * 8
DOUT_N = CLBN * 8

print('''
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
f.write('module,loc,n\n')
slices = gen_slicems()
print('module roi(input clk, input [%d:0] din, output [%d:0] dout);' % (DIN_N - 1, DOUT_N - 1))
for i in range(CLBN):
    module = 'my_RAM64X1D_N'
    try:
        loc, loc_pos = next(slices)
    except StopIteration:
        break
    n = 2

    print('    %s' % module)
    print('            #(.LOC("%s"), .N(%d))' % (loc, n))
    print('            clb_%d (.clk(clk), .din(din[  %d +: 8]), .dout(dout[  %d +: 8]));' % (i, 8 * i, 8 * i))

    f.write('%s,%s,%s\n' % (module, loc, n))
f.close()
print('''endmodule

// ---------------------------------------------------------------------

''')

print('''
module my_RAM64X1D_N (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    parameter N = 1;

    generate
        if (N >= 2) begin
            (* LOC=LOC *)
            RAM64X1D #(
                    .INIT(64'h0),
                    .IS_WCLK_INVERTED(1'b0)
                ) ramb (
                    .DPO(dout[1]),
                    .D(din[0]),
                    .WCLK(clk),
                    .WE(din[2]),
                    .A0(din[3]),
                    .A1(din[4]),
                    .A2(din[5]),
                    .A3(din[6]),
                    .A4(din[7]),
                    .A5(din[0]),
                    .DPRA0(din[1]),
                    .DPRA1(din[2]),
                    .DPRA2(din[3]),
                    .DPRA3(din[4]),
                    .DPRA4(din[5]),
                    .DPRA5(din[6]));
        end

        if (N >= 1) begin
            (* LOC=LOC *)
            RAM64X1D #(
                    .INIT(64'h0),
                    .IS_WCLK_INVERTED(1'b0)
                ) rama (
                    .DPO(dout[0]),
                    .D(din[0]),
                    .WCLK(clk),
                    .WE(din[2]),
                    .A0(din[3]),
                    .A1(din[4]),
                    .A2(din[5]),
                    .A3(din[6]),
                    .A4(din[7]),
                    .A5(din[0]),
                    .DPRA0(din[1]),
                    .DPRA1(din[2]),
                    .DPRA2(din[3]),
                    .DPRA3(din[4]),
                    .DPRA4(din[5]),
                    .DPRA5(din[6]));
        end
    endgenerate
endmodule
''')

