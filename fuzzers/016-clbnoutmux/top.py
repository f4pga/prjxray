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
slices = gen_slices()
print('module roi(input clk, input [%d:0] din, output [%d:0] dout);' % (DIN_N - 1, DOUT_N - 1))
for i in range(CLBN):
    # Don't have an O6 example
    modules = ['clb_NOUTMUX_' + x for x in ['CY', 'F78', 'O5', 'XOR', 'B5Q']]
    module = random.choice(modules)

    if module == 'clb_NOUTMUX_F78':
        n = random.randint(0, 2)
    else:
        n = random.randint(0, 3)
    #n = 0
    loc = next(slices)

    print('    %s' % module)
    print('            #(.LOC("%s"), .N(%d))' % (loc, n))
    print('            clb_%d (.clk(clk), .din(din[  %d +: 8]), .dout(dout[  %d +: 8]));' % (i, 8 * i, 8 * i))

    f.write('%s,%s,%s\n' % (module, loc, n))
f.close()
print('''endmodule

// ---------------------------------------------------------------------

''')

print('''
module myLUT8 (input clk, input [7:0] din,
        output lut8o, output lut7bo, output lut7ao,
        //caro: XOR additional result (main output)
        //carco: CLA result (carry module additional output)
        output caro, output carco,
        output bo5, output bo6,
        //Note: b5ff_q requires the mux and will conflict with other wires
        //Otherwise this FF drops out
        output wire ff_q);
        //output wire [3:0] n5ff_q);
    parameter N=-1;
    parameter LOC="SLICE_FIXME";

    wire [3:0] caro_all;
    assign caro = caro_all[N];
    wire [3:0] carco_all;
    assign carco = carco_all[N];

    wire [3:0] lutno6;
    assign bo6 = lutno6[N];
    wire [3:0] lutno5;
    assign bo5 = lutno5[N];

    //Outputs does not have to be used, will stay without it
    (* LOC=LOC, BEL="F8MUX", KEEP, DONT_TOUCH *)
    MUXF8 mux8 (.O(lut8o), .I0(lut7bo), .I1(lut7ao), .S(din[6]));
    (* LOC=LOC, BEL="F7BMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7b (.O(lut7bo), .I0(lutno6[3]), .I1(lutno6[2]), .S(din[6]));
    (* LOC=LOC, BEL="F7AMUX", KEEP, DONT_TOUCH *)
    MUXF7 mux7a (.O(lut7ao), .I0(lutno6[1]), .I1(lutno6[0]), .S(din[6]));

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
		.O5(lutno5[3]),
		.O6(lutno6[3]));

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
		.O5(lutno5[2]),
		.O6(lutno6[2]));

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
		.O5(lutno5[1]),
		.O6(lutno6[1]));

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
		.O5(lutno5[0]),
		.O6(lutno6[0]));

    //Outputs do not have to be used, will stay without them
	(* LOC=LOC, KEEP, DONT_TOUCH *)
    CARRY4 carry4(.O(caro_all), .CO(carco_all), .DI(lutno5), .S(lutno6), .CYINIT(1'b0), .CI());

    generate
        if (N == 3) begin
	        (* LOC=LOC, BEL="D5FF", KEEP, DONT_TOUCH *)
	        FDPE d5ff (
		        .C(clk),
		        .Q(ff_q),
		        .CE(1'b1),
		        .PRE(1'b0),
		        .D(lutno5[3]));
        end
        if (N == 2) begin
	        (* LOC=LOC, BEL="C5FF", KEEP, DONT_TOUCH *)
	        FDPE c5ff (
		        .C(clk),
		        .Q(ff_q),
		        .CE(1'b1),
		        .PRE(1'b0),
		        .D(lutno5[2]));
        end
        if (N == 1) begin
	        (* LOC=LOC, BEL="B5FF", KEEP, DONT_TOUCH *)
	        FDPE b5ff (
		        .C(clk),
		        .Q(ff_q),
		        .CE(1'b1),
		        .PRE(1'b0),
		        .D(lutno5[1]));
        end
        if (N == 0) begin
	        (* LOC=LOC, BEL="A5FF", KEEP, DONT_TOUCH *)
	        FDPE a5ff (
		        .C(clk),
		        .Q(ff_q),
		        .CE(1'b1),
		        .PRE(1'b0),
		        .D(lutno5[0]));
        end
    endgenerate
endmodule

//******************************************************************************
//BOUTMUX tests

module clb_NOUTMUX_CY (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=1;

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din), .lut8o(),
            .caro(), .carco(dout[0]),
            .bo5(), .bo6(),
            .ff_q());
endmodule

//clb_NOUTMUX_F78: already have above as clb_LUT8
module clb_NOUTMUX_F78 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=1;
    wire lut8o, lut7bo, lut7ao;
    /*
    D: N/A (no such mux position)
    C: F7B:O
    B: F8:O
    A: F7A:O
    */
    generate
        if (N == 3) begin
            //No muxes, so this is undefined
           invalid_configuration invalid_configuration3();
        end else if (N == 2) begin
            assign dout[0] = lut7bo;
        end else if (N == 1) begin
            assign dout[0] = lut8o;
        end else if (N == 0) begin
            assign dout[0] = lut7ao;
        end
    endgenerate

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din),
            .lut8o(lut8o), .lut7bo(lut7bo), .lut7ao(lut7ao),
            .caro(), .carco(),
            .bo5(), .bo6(),
            .ff_q());
endmodule

module clb_NOUTMUX_O5 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=1;

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din), .lut8o(),
            .caro(), .carco(),
            .bo5(dout[0]), .bo6(),
            .ff_q());
endmodule

/*
//FIXME: need to force it to use both X and O6
module clb_NOUTMUX_O6 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=1;

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din), .lut8o(), .co(), .carco(), .bo5(), .bo6());
endmodule
*/

module clb_NOUTMUX_XOR (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=1;

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din), .lut8o(),
            .caro(dout[0]), .carco(),
            .bo5(), .bo6(),
            .ff_q());
endmodule

module clb_NOUTMUX_B5Q (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=1;

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din),
            .lut8o(),
            .caro(), .carco(),
            .bo5(), .bo6(),
            .ff_q(dout[0]));
endmodule
''')

