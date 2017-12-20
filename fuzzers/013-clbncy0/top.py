import random

random.seed(0)

CLBN = 400
# SLICE_X12Y100
# SLICE_X27Y149
SLICEX = (12, 28)
SLICEY = (100, 150)
# 800
SLICEN = (SLICEY[1] - SLICEY[0]) * (SLICEX[1] - SLICEX[0])
print('//SLICEX: %s' % str(SLICEX))
print('//SLICEY: %s' % str(SLICEY))
print('//SLICEN: %s' % str(SLICEN))
print('//Requested CLBs: %s' % str(CLBN))

def gen_slices():
    for slicey in range(*SLICEY):
        for slicex in range(*SLICEX):
            yield "SLICE_X%dY%d" % (slicex, slicey)

DIN_N = CLBN * 8
DOUT_N = CLBN * 8

lut_bels = ['A6LUT', 'B6LUT', 'C6LUT', 'D6LUT']

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
f.write('module,loc,bel,n\n')
slices = gen_slices()
print('module roi(input clk, input [%d:0] din, output [%d:0] dout);' % (DIN_N - 1, DOUT_N - 1))
for i in range(CLBN):
    bel = ''

    if random.randint(0, 1):
        module = 'clb_NCY0_MX'
    else:
        module = 'clb_NCY0_O5'
    n = random.randint(0, 3)
    loc = next(slices)
    bel = lut_bels[n]

    print('    %s' % module)
    print('            #(.LOC("%s"), .BEL("%s"), .N(%d))' % (loc, bel, n))
    print('            clb_%d (.clk(clk), .din(din[  %d +: 8]), .dout(dout[  %d +: 8]));' % (i, 8 * i, 8 * i))

    f.write('%s,%s,%s,%s\n' % (module, loc, bel, n))
f.close()
print('''endmodule

// ---------------------------------------------------------------------

''')

print('''
module clb_NCY0_MX (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X16Y129_FIXME";
    parameter BEL="A6LUT_FIXME";
    parameter N=-1;

    wire [3:0] o;
    assign dout[0] = o[1];
    wire o6, o5;
    reg [3:0] s;

    always @(*) begin
        s = din[7:4];
        s[N] = o6;
    end

	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_0000_0000_0001)
	) lut (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(o5),
		.O6(o6));

	(* LOC=LOC, KEEP, DONT_TOUCH *)
    CARRY4 carry4(.O(o), .CO(), .DI(din[3:0]), .S(s), .CYINIT(1'b0), .CI());
endmodule

module clb_NCY0_O5 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X16Y129_FIXME";
    parameter BEL="A6LUT_FIXME";
    parameter N=-1;

    wire [3:0] o;
    assign dout[0] = o[1];
    wire o6, o5;
    reg [3:0] s;
    reg [3:0] di;

    always @(*) begin
        s = din[7:4];
        s[N] = o6;
        
        di = {din[3:0]};
        di[N] = o5;
    end

	(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_0000_0000_0001)
	) lut (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(o5),
		.O6(o6));

	(* LOC=LOC, KEEP, DONT_TOUCH *)
    CARRY4 carry4(.O(o), .CO(), .DI(di), .S(s), .CYINIT(1'b0), .CI());
endmodule
''')

