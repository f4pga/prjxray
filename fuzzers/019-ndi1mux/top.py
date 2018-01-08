import random
random.seed(0)
import os
import re

def slice_xy():
    '''Return (X1, X2), (Y1, Y2) from XRAY_ROI, exclusive end (for xrange)'''
    # SLICE_X12Y100:SLICE_X27Y149
    # Note XRAY_ROI_GRID_* is something else
    m = re.match(r'SLICE_X([0-9]*)Y([0-9]*):SLICE_X([0-9]*)Y([0-9]*)', os.getenv('XRAY_ROI'))
    ms = [int(m.group(i + 1)) for i in range(4)]
    return ((ms[0], ms[2] + 1), (ms[1], ms[3] + 1))

CLBN = 50
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
    for slicex in (12, 14):
        for slicey in range(*SLICEY):
            # caller may reject position if needs more room
            #yield ("SLICE_X%dY%d" % (slicex, slicey), (slicex, slicey))
            yield "SLICE_X%dY%d" % (slicex, slicey)


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
f.write('module,loc,c31,b31,a31\n')
slices = gen_slicems()
print('module roi(input clk, input [%d:0] din, output [%d:0] dout);' % (DIN_N - 1, DOUT_N - 1))
multis = 0
for clbi in range(CLBN):
    loc = next(slices)
    module = 'my_NDI1MUX_NI_NMC31'
    c31 = random.randint(0, 1)
    b31 = random.randint(0, 1)
    a31 = random.randint(0, 1)

    print('    %s' % module)
    print('           #(.LOC("%s"), .C31(%d), .B31(%d), .A31(%d))' % (loc, c31, b31, a31))
    print('            clb_%d (.clk(clk), .din(din[  %d +: 8]), .dout(dout[  %d +: 8]));' % (clbi, 8 * clbi, 8 * clbi))

    f.write('%s,%s,%d,%d,%d\n' % (module, loc, c31, b31, a31))
f.close()
print('''endmodule

// ---------------------------------------------------------------------

''')

print('''
module my_NDI1MUX_NI_NMC31 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "SLICE_X6Y100";
    parameter C31 = 0;
    parameter B31 = 0;
    parameter A31 = 0;

    wire [3:0] q31;

    wire [3:0] lutd;
    assign lutd[3] = din[7];
    assign lutd[2] = C31 ? q31[3] : din[7];
    assign lutd[1] = B31 ? q31[2] : din[7];
    assign lutd[0] = A31 ? q31[1] : din[7];

    (* LOC=LOC, BEL="D6LUT" *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutd (
            .Q(dout[0]),
            .Q31(q31[3]),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(lutd[3]));
    (* LOC=LOC, BEL="C6LUT" *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutc (
            .Q(dout[1]),
            .Q31(q31[2]),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(lutd[2]));
    (* LOC=LOC, BEL="B6LUT" *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lutb (
            .Q(dout[2]),
            .Q31(q31[1]),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(lutd[1]));
    (* LOC=LOC, BEL="A6LUT" *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) luta (
            .Q(dout[3]),
            .Q31(q31[0]),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(lutd[0]));
endmodule
''')

