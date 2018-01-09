import random
random.seed(0)
import os
import re


def slice_xy():
    '''Return (X1, X2), (Y1, Y2) from XRAY_ROI, exclusive end (for xrange)'''
    # SLICE_X12Y100:SLICE_X27Y149
    # Note XRAY_ROI_GRID_* is something else
    m = re.match(
        r'SLICE_X([0-9]*)Y([0-9]*):SLICE_X([0-9]*)Y([0-9]*)', os.getenv('XRAY_ROI'))
    ms = [int(m.group(i + 1)) for i in range(4)]
    return ((ms[0], ms[2] + 1), (ms[1], ms[3] + 1))


CLBN = 40
SLICEX, SLICEY = slice_xy()
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
f.write('module,loc,n,def_a\n')
slices = gen_slices()
print('module roi(input clk, input [%d:0] din, output [%d:0] dout);' % (
    DIN_N - 1, DOUT_N - 1))
for i in range(CLBN):
    bel = ''

    module = 'clb_N5FFMUX'
    n = random.randint(0, 3)
    def_a = random.randint(0, 1)
    loc = next(slices)

    print('    %s' % module)
    print('            #(.LOC("%s"), .N(%d), .DEF_A(%d))' % (loc, n, def_a))
    print(
        '            clb_%d (.clk(clk), .din(din[  %d +: 8]), .dout(dout[  %d +: 8]));' % (i, 8 * i, 8 * i))

    f.write('%s,%s,%s,%s\n' % (module, loc, n, def_a))
f.close()
print('''endmodule

// ---------------------------------------------------------------------

''')

print('''
module clb_N5FFMUX (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X22Y100";
    parameter N=-1;
    parameter DEF_A=1;
    wire lutdo, lutco, lutbo, lutao;
    wire lut7bo, lut7ao;
    wire lut8o;

    reg [3:0] ffds;
    wire lutdo5, lutco5, lutbo5, lutao5;
    //wire lutno5 [3:0] = {lutao5, lutbo5, lutco5, lutdo5};
    wire lutno5 [3:0] = {lutdo5, lutco5, lutbo5, lutao5};
    always @(*) begin
        if (DEF_A) begin
            //Default poliarty A
            ffds[3] = lutdo5;
            ffds[2] = lutco5;
            ffds[1] = lutbo5;
            ffds[0] = lutao5;
            ffds[N] = din[6];
        end else begin
            //Default polarity B
            ffds[3] = din[6];
            ffds[2] = din[6];
            ffds[1] = din[6];
            ffds[0] = din[6];
            ffds[N] = lutno5[N];
        end
    end

    (* LOC=LOC, BEL="F8MUX", KEEP, DONT_TOUCH *)
    MUXF8 mux8 (.O(), .I0(lut7bo), .I1(lut7ao), .S(din[6]));
    (* LOC=LOC, BEL="F7BMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7b (.O(lut7bo), .I0(lutdo), .I1(lutco), .S(din[6]));
    (* LOC=LOC, BEL="F7AMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7a (.O(lut7ao), .I0(lutbo), .I1(lutao), .S(din[6]));

	(* LOC=LOC, BEL="D6LUT", KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_DEAD_0000_0001)
	) lutd (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(lutdo5),
		.O6(lutdo));
	(* LOC=LOC, BEL="D5FF" *)
	FDPE ffd (
		.C(clk),
		.Q(dout[1]),
		.CE(din[0]),
		.PRE(din[1]),
		.D(ffds[3]));

	(* LOC=LOC, BEL="C6LUT", KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_BEEF_0000_0001)
	) lutc (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(lutco5),
		.O6(lutco));
	(* LOC=LOC, BEL="C5FF" *)
	FDPE ffc (
		.C(clk),
		.Q(dout[2]),
		.CE(din[0]),
		.PRE(din[1]),
		.D(ffds[2]));

	(* LOC=LOC, BEL="B6LUT", KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_CAFE_0000_0001)
	) lutb (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(lutbo5),
		.O6(lutbo));
	(* LOC=LOC, BEL="B5FF" *)
	FDPE ffb (
		.C(clk),
		.Q(dout[3]),
		.CE(din[0]),
		.PRE(din[1]),
		.D(ffds[1]));

	(* LOC=LOC, BEL="A6LUT", KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_1CE0_0000_0001)
	) luta (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(lutao5),
		.O6(lutao));
	(* LOC=LOC, BEL="A5FF" *)
	FDPE ffa (
		.C(clk),
		.Q(dout[4]),
		.CE(din[0]),
		.PRE(din[1]),
		//D can only come from O5 or AX
		//AX is used by MUXF7:S
		.D(ffds[0]));
endmodule
''')
