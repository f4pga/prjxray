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
f.write('module,loc,bela,belb,belc,beld\n')
slices = gen_slicems()
print('module roi(input clk, input [%d:0] din, output [%d:0] dout);' % (DIN_N - 1, DOUT_N - 1))
multis = 0
for clbi in range(CLBN):
    bel = ''

    # Can fit 4 per CLB
    # BELable
    multi_bels_by = [
        'SRL16E',
        'SRLC32E',
        'LUT6',
        ]
    # Not BELable
    multi_bels_bn = [
        'RAM32X1S',
        'RAM64X1S',
        ]

    # Those requiring special resources
    # Just make one per module
    greedy_modules = [
        'my_RAM128X1D',
        'my_RAM128X1S',
        'my_RAM256X1S',
        ]

    loc = next(slices)

    params = ''
    cparams = ''
    # Multi module
    if random.randint(0, 3) > 0:
        params = ''
        module = 'my_ram_N'

        # Pick one un-LOCable and then fill in with LOCable
        '''
        CRITICAL WARNING: [Constraints 18-5] Cannot loc instance '\''roi/clb_2/lutd'\'' 
        at site SLICE_X12Y102, Instance roi/clb_2/lutd can not be placed in D6LUT 
        of site SLICE_X12Y102 because the bel is occupied by roi/clb_2/RAM64X1S/SP(port:). 
        This could be caused by bel constraint conflict

        Hmm I guess they have to go in LUTD after all
        Unclear to me why this is
        '''
        #unbel_beli = random.randint(0, 3)
        unbel_beli = 3
        if random.randint(0, 1):
            unbel_beli = None
        bels = []
        for beli in range(4):
            belc = chr(ord('A') + beli)
            if beli == unbel_beli:
                # Chose a BEL instance that will get implicitly placed
                bel = random.choice(multi_bels_bn)
                params += ', .N_%s(1)' % bel
            else:
                bel = random.choice(multi_bels_by)
                if multis % 4 == 0:
                    # Force an all LUT6 SLICE
                    bel = 'LUT6'
                params += ', .%c_%s(1)' % (belc, bel)

            bels.append(bel)
        # Record the BELs we chose in the module (A, B, C, D)
        cparams = ',' + (','.join(bels))
        multis += 1
    # Greedy module
    # Don't place anything else in it
    # For solving muxes vs previous results
    else:
        module = random.choice(greedy_modules)
        params = ''
        cparams = ',,,,'

    print('    %s' % module)
    print('            #(.LOC("%s")%s)' % (loc, params))
    print('            clb_%d (.clk(clk), .din(din[  %d +: 8]), .dout(dout[  %d +: 8]));' % (clbi, 8 * clbi, 8 * clbi))

    f.write('%s,%s%s\n' % (module, loc, cparams))
f.close()
print('''endmodule

// ---------------------------------------------------------------------

''')

print('''

//***************************************************************
//Supermodule

//BEL: yes
module my_ram_N (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    parameter D_SRL16E=0;
    parameter D_SRLC32E=0;
    parameter D_LUT6=0;

    parameter C_SRL16E=0;
    parameter C_SRLC32E=0;
    parameter C_LUT6=0;

    parameter B_SRL16E=0;
    parameter B_SRLC32E=0;
    parameter B_LUT6=0;

    parameter A_SRL16E=0;
    parameter A_SRLC32E=0;
    parameter A_LUT6=0;

    parameter N_RAM32X1S=0;
    parameter N_RAM64X1S=0;
    
    parameter SRLINIT = 32'h00000000;
    //parameter LUTINIT6 = 64'h0000_0000_0000_0000;
    parameter LUTINIT6 = 64'hFFFF_FFFF_FFFF_FFFF;

    wire ce = din[4];

    generate
        if (D_SRL16E) begin
            (* LOC=LOC, BEL="D6LUT", KEEP, DONT_TOUCH *)
            SRL16E #(
                ) lutd (
                    .Q(dout[3]),
                    .A0(din[0]),
                    .A1(din[1]),
                    .A2(din[2]),
                    .A3(din[3]),
                    .CE(ce),
                    .CLK(clk),
                    .D(din[6]));
        end
        if (D_SRLC32E) begin
            (* LOC=LOC, BEL="D6LUT", KEEP, DONT_TOUCH *)
            SRLC32E #(
                    .INIT(SRLINIT),
                    .IS_CLK_INVERTED(1'b0)
                ) lutd (
                    .Q(dout[3]),
                    .Q31(),
                    .A(din[4:0]),
                    .CE(ce),
                    .CLK(clk),
                    .D(din[7]));
        end
        if (D_LUT6) begin
	        (* LOC=LOC, BEL="D6LUT", KEEP, DONT_TOUCH *)
	        LUT6_2 #(
		        .INIT(LUTINIT6)
	        ) lutd (
		        .I0(din[0]),
		        .I1(din[1]),
		        .I2(din[2]),
		        .I3(din[3]),
		        .I4(din[4]),
		        .I5(din[5]),
		        .O5(),
		        .O6(dout[3]));
        end

        if (C_SRL16E) begin
            (* LOC=LOC, BEL="C6LUT", KEEP, DONT_TOUCH *)
            SRL16E #(
                ) lutc (
                    .Q(dout[2]),
                    .A0(din[0]),
                    .A1(din[1]),
                    .A2(din[2]),
                    .A3(din[3]),
                    .CE(ce),
                    .CLK(clk),
                    .D(din[6]));
        end
        if (C_SRLC32E) begin
            (* LOC=LOC, BEL="C6LUT", KEEP, DONT_TOUCH *)
            SRLC32E #(
                    .INIT(SRLINIT),
                    .IS_CLK_INVERTED(1'b0)
                ) lutc (
                    .Q(dout[2]),
                    .Q31(),
                    .A(din[4:0]),
                    .CE(ce),
                    .CLK(clk),
                    .D(din[7]));
        end
        if (C_LUT6) begin
	        (* LOC=LOC, BEL="C6LUT", KEEP, DONT_TOUCH *)
	        LUT6_2 #(
		        .INIT(LUTINIT6)
	        ) lutc (
		        .I0(din[0]),
		        .I1(din[1]),
		        .I2(din[2]),
		        .I3(din[3]),
		        .I4(din[4]),
		        .I5(din[5]),
		        .O5(),
		        .O6(dout[2]));
        end

        if (B_SRL16E) begin
            (* LOC=LOC, BEL="B6LUT", KEEP, DONT_TOUCH *)
            SRL16E #(
                ) lutb (
                    .Q(dout[1]),
                    .A0(din[0]),
                    .A1(din[1]),
                    .A2(din[2]),
                    .A3(din[3]),
                    .CE(ce),
                    .CLK(clk),
                    .D(din[6]));
        end
        if (B_SRLC32E) begin
            (* LOC=LOC, BEL="B6LUT", KEEP, DONT_TOUCH *)
            SRLC32E #(
                    .INIT(SRLINIT),
                    .IS_CLK_INVERTED(1'b0)
                ) lutb (
                    .Q(dout[1]),
                    .Q31(),
                    .A(din[4:0]),
                    .CE(ce),
                    .CLK(clk),
                    .D(din[7]));
        end
        if (B_LUT6) begin
	        (* LOC=LOC, BEL="B6LUT", KEEP, DONT_TOUCH *)
	        LUT6_2 #(
		        .INIT(LUTINIT6)
	        ) lutb (
		        .I0(din[0]),
		        .I1(din[1]),
		        .I2(din[2]),
		        .I3(din[3]),
		        .I4(din[4]),
		        .I5(din[5]),
		        .O5(),
		        .O6(dout[1]));
        end

        if (A_SRL16E) begin
            (* LOC=LOC, BEL="A6LUT", KEEP, DONT_TOUCH *)
            SRL16E #(
                ) luta (
                    .Q(dout[0]),
                    .A0(din[0]),
                    .A1(din[1]),
                    .A2(din[2]),
                    .A3(din[3]),
                    .CE(ce),
                    .CLK(clk),
                    .D(din[6]));
        end
        if (A_SRLC32E) begin
            (* LOC=LOC, BEL="A6LUT", KEEP, DONT_TOUCH *)
            SRLC32E #(
                    .INIT(SRLINIT),
                    .IS_CLK_INVERTED(1'b0)
                ) luta (
                    .Q(dout[0]),
                    .Q31(),
                    .A(din[4:0]),
                    .CE(ce),
                    .CLK(clk),
                    .D(din[7]));
        end
        if (A_LUT6) begin
	        (* LOC=LOC, BEL="A6LUT", KEEP, DONT_TOUCH *)
	        LUT6_2 #(
		        .INIT(LUTINIT6)
	        ) luta (
		        .I0(din[0]),
		        .I1(din[1]),
		        .I2(din[2]),
		        .I3(din[3]),
		        .I4(din[4]),
		        .I5(din[5]),
		        .O5(),
		        .O6(dout[0]));
        end

        if (N_RAM32X1S) begin
            (* LOC=LOC, KEEP, DONT_TOUCH *)
            RAM32X1S #(
                ) RAM32X1S (
                    .O(dout[4]),
                    .A0(din[0]),
                    .A1(din[1]),
                    .A2(din[2]),
                    .A3(din[3]),
                    .A4(din[4]),
                    .D(din[5]),
                    .WCLK(clk),
                    .WE(ce));
        end
        if (N_RAM64X1S) begin
            (* LOC=LOC, KEEP, DONT_TOUCH *)
            RAM64X1S #(
                ) RAM64X1S (
                    .O(dout[4]),
                    .A0(din[0]),
                    .A1(din[1]),
                    .A2(din[2]),
                    .A3(din[3]),
                    .A4(din[4]),
                    .A5(din[5]),
                    .D(din[6]),
                    .WCLK(clk),
                    .WE(ce));
        end
    endgenerate
endmodule


//***************************************************************
//Basic

//BEL: yes
module my_SRL16E (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    parameter BEL="A6LUT";

    (* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
    SRL16E #(
        ) SRL16E (
            .Q(dout[0]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .CE(din[4]),
            .CLK(din[5]),
            .D(din[6]));
endmodule

//BEL: yes
module my_SRLC32E (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";
    parameter BEL="A6LUT";

    wire mc31c;

    (* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
    SRLC32E #(
            .INIT(32'h00000000),
            .IS_CLK_INVERTED(1'b0)
        ) lut (
            .Q(dout[0]),
            .Q31(mc31c),
            .A(din[4:0]),
            .CE(din[5]),
            .CLK(din[6]),
            .D(din[7]));
endmodule

//BEL: can't
module my_RAM32X1S (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM32X1S #(
        ) RAM32X1S (
            .O(dout[0]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .D(din[5]),
            .WCLK(din[6]),
            .WE(din[7]));
endmodule

//BEL: can't
module my_RAM64X1S (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM64X1S #(
        ) RAM64X1S (
            .O(dout[0]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .A5(din[5]),
            .D(din[6]),
            .WCLK(clk),
            .WE(din[0]));
endmodule

//***************************************************************
//WA*USED

//Dedicated LOC
module my_RAM128X1D (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM128X1D #(
            .INIT(128'h0),
            .IS_WCLK_INVERTED(1'b0)
        ) RAM128X1D (
            .DPO(dout[0]),
            .SPO(dout[1]),
            .D(din[0]),
            .WCLK(clk),
            .WE(din[2]));
endmodule

//Dedicated LOC
module my_RAM128X1S (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM128X1S #(
        ) RAM128X1S (
            .O(dout[0]),
            .A0(din[0]),
            .A1(din[1]),
            .A2(din[2]),
            .A3(din[3]),
            .A4(din[4]),
            .A5(din[5]),
            .A6(din[6]),
            .D(din[7]),
            .WCLK(din[0]),
            .WE(din[1]));
endmodule

//Dedicated LOC
module my_RAM256X1S (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC, KEEP, DONT_TOUCH *)
    RAM256X1S #(
        ) RAM256X1S (
            .O(dout[0]),
            .A({din[0], din[7:0]}),
            .D(din[0]),
            .WCLK(din[1]),
            .WE(din[2]));
endmodule
''')

