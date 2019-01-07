module top(input clk, stb, di, output do);
    localparam integer DIN_N = 256;
    localparam integer DOUT_N = 256;

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

module roi(input clk, input [255:0] din, output [255:0] dout);
    parameter N=0;

    clb_NFFMUX_AX #(.LOC("SLICE_X18Y100"), .N(N))
            clb_NFFMUX_AX       (.clk(clk), .din(din[  8 +: 8]), .dout(dout[  8 +: 8]));
    clb_NFFMUX_CY #(.LOC("SLICE_X18Y101"), .N(N))
            clb_NFFMUX_CY       (.clk(clk), .din(din[  16 +: 8]), .dout(dout[  16 +: 8]));
    generate
        if (N != 3) begin
            clb_NFFMUX_F78 #(.LOC("SLICE_X18Y102"), .N(N))
                    clb_NFFMUX_F78       (.clk(clk), .din(din[  24 +: 8]), .dout(dout[  24 +: 8]));
        end
    endgenerate
    clb_NFFMUX_O5 #(.LOC("SLICE_X18Y103"), .N(N))
            clb_NFFMUX_O5       (.clk(clk), .din(din[  32 +: 8]), .dout(dout[  32 +: 8]));
    clb_NFFMUX_O6 #(.LOC("SLICE_X18Y104"), .N(N))
            clb_NFFMUX_O6     (.clk(clk), .din(din[  40 +: 8]), .dout(dout[  40 +: 8]));
    clb_NFFMUX_XOR #(.LOC("SLICE_X18Y105"), .N(N))
            clb_NFFMUX_XOR     (.clk(clk), .din(din[  48 +: 8]), .dout(dout[ 48 +: 8 ]));
endmodule

module myLUT8 (input clk, input [7:0] din,
        output lut8o, output lut7bo, output lut7ao,
        //caro: XOR additional result (main output)
        //carco: CLA result (carry module additional output)
        output caro, output carco,
        output bo5, output bo6,
        output wire ff_q, //always connect to output
        input wire ff_d); //mux output net
    parameter LOC="SLICE_FIXME";
    parameter N=-1;

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
            (* LOC=LOC, BEL="DFF", KEEP, DONT_TOUCH *)
            FDPE bff (
                .C(clk),
                .Q(ff_q),
                .CE(1'b1),
                .PRE(1'b0),
                .D(ff_d));
        end
        if (N == 2) begin
            (* LOC=LOC, BEL="CFF", KEEP, DONT_TOUCH *)
            FDPE bff (
                .C(clk),
                .Q(ff_q),
                .CE(1'b1),
                .PRE(1'b0),
                .D(ff_d));
        end
        if (N == 1) begin
            (* LOC=LOC, BEL="BFF", KEEP, DONT_TOUCH *)
            FDPE bff (
                .C(clk),
                .Q(ff_q),
                .CE(1'b1),
                .PRE(1'b0),
                .D(ff_d));
        end
        if (N == 0) begin
            (* LOC=LOC, BEL="AFF", KEEP, DONT_TOUCH *)
            FDPE bff (
                .C(clk),
                .Q(ff_q),
                .CE(1'b1),
                .PRE(1'b0),
                .D(ff_d));
        end
    endgenerate
endmodule

//******************************************************************************
//BFFMUX tests

module clb_NFFMUX_AX (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=-1;

    /*
    D: DX
        drawn a little differently
        not a mux control
        becomes a dedicated external signal
    C: CX
    B: BX
    A: AX
    */
    wire ax = din[6]; //used on MUX8:S, MUX7A:S, and MUX7B:S

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din),
            .lut8o(),
            .caro(), .carco(),
            .bo5(), .bo6(),
            .ff_q(dout[0]),
            .ff_d(ax));

endmodule

module clb_NFFMUX_CY (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=-1;
    wire carco;

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din),
            .lut8o(),
            .caro(), .carco(carco),
            .bo5(), .bo6(),
            .ff_q(dout[0]),
            .ff_d(carco));
endmodule

module clb_NFFMUX_F78 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=-1;
    wire lut8o, lut7bo, lut7ao;

    /*
    D: N/A (no such mux position)
    C: F7B:O
    B: F8:O
    A: F7A:O
    */
    wire ff_d;

    generate
        if (N == 3) begin
            //No muxes, so this is undefined
           invalid_configuration invalid_configuration3();
        end else if (N == 2) begin
            assign ff_d = lut7bo;
        end else if (N == 1) begin
            assign ff_d = lut8o;
        end else if (N == 0) begin
            assign ff_d = lut7ao;
        end
    endgenerate

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din),
            .lut8o(lut8o), .lut7bo(lut7bo), .lut7ao(lut7ao),
            .caro(), .carco(),
            .bo5(), .bo6(),
            .ff_q(dout[0]),
            .ff_d(ff_d));
endmodule

module clb_NFFMUX_O5 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=-1;
    wire bo5;

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din),
            .lut8o(),
            .caro(), .carco(),
            .bo5(bo5), .bo6(),
            .ff_q(dout[0]),
            .ff_d(bo5));
endmodule

module clb_NFFMUX_O6 (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=-1;
    wire bo6;

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din),
            .lut8o(),
            .caro(), .carco(),
            .bo5(), .bo6(bo6),
            .ff_q(dout[0]),
            .ff_d(bo6));
endmodule

module clb_NFFMUX_XOR (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_FIXME";
    parameter N=-1;
    wire caro;

    myLUT8 #(.LOC(LOC), .N(N))
            myLUT8(.clk(clk), .din(din),
            .lut8o(),
            .caro(caro), .carco(),
            .bo5(), .bo6(bo6),
            .ff_q(dout[0]),
            .ff_d(caro));
endmodule

