`include "src/rom.v"
`include "src/serializer.v"
`include "src/transmitter.v"
`include "src/receiver.v"
`include "src/comparator.v"
`include "src/trx_path.v"

`default_nettype none

// ============================================================================

module top
(
input  wire clk,

input  wire rx,
output wire tx,

input  wire [15:0] sw,
output wire [15:0] led,

output wire ja1,
output wire ja2,
output wire ja3,
output wire ja4,
input  wire ja7,
input  wire ja8,
input  wire ja9,
input  wire ja10,

output wire jb1,
output wire jb2,
output wire jb3,
output wire jb4,
input  wire jb7,
input  wire jb8,
input  wire jb9,
input  wire jb10,

output wire jc1,
output wire jc2,
output wire jc3,
output wire jc4,
input  wire jc7,
input  wire jc8,
input  wire jc9,
input  wire jc10
);

// ============================================================================
// Clock & reset
// Divide the input clock to allow for less strict timing requirements.
reg [3:0] rst_sr;
reg [7:0] clk_ps;

initial rst_sr <= 4'hF;
initial clk_ps <= 0;

always @(posedge clk)
    if (sw[0])
        rst_sr <= 4'hF;
    else
        rst_sr <= rst_sr >> 1;

always @(posedge clk)
    clk_ps <= clk_ps + 1;

wire CLK100 = clk;
wire CLK = clk_ps[2];
wire RST = rst_sr[0];

// ============================================================================
// ISERDES test logic
wire [9:0] error;
wire [9:0] data;

wire s_clk;

// ........

trx_path #
(
.WIDTH  (2),
.MODE   ("SDR")
)
path_sdr_2
(
.CLK    (CLK),
.RST    (RST),
.O_DAT  (data[0]),
.O_CLK  (s_clk),
.I_DAT  (jb7),
.ERROR  (error[0])
);

trx_path #
(
.WIDTH  (3),
.MODE   ("SDR")
)
path_sdr_3
(
.CLK    (CLK),
.RST    (RST),
.O_DAT  (data[1]),
.I_DAT  (jb8),
.ERROR  (error[1])
);

trx_path #
(
.WIDTH  (4),
.MODE   ("SDR")
)
path_sdr_4
(
.CLK    (CLK),
.RST    (RST),
.O_DAT  (data[2]),
.I_DAT  (jb9),
.ERROR  (error[2])
);

trx_path #
(
.WIDTH  (5),
.MODE   ("SDR")
)
path_sdr_5
(
.CLK    (CLK),
.RST    (RST),
.O_DAT  (data[3]),
.I_DAT  (jb10),
.ERROR  (error[3])
);

// ........

trx_path #
(
.WIDTH  (6),
.MODE   ("SDR")
)
path_sdr_6
(
.CLK    (CLK),
.RST    (RST),
.O_DAT  (data[4]),
.I_DAT  (jc7),
.ERROR  (error[4])
);

trx_path #
(
.WIDTH  (7),
.MODE   ("SDR")
)
path_sdr_7
(
.CLK    (CLK),
.RST    (RST),
.O_DAT  (data[5]),
.I_DAT  (jc8),
.ERROR  (error[5])
);

trx_path #
(
.WIDTH  (8),
.MODE   ("SDR")
)
path_sdr_8
(
.CLK    (CLK),
.RST    (RST),
.O_DAT  (data[6]),
.I_DAT  (jc9),
.ERROR  (error[6])
);

trx_path #
(
.WIDTH  (4),
.MODE   ("DDR")
)
path_ddr_4
(
.CLK    (CLK),
.RST    (RST),
.O_DAT  (data[7]),
.I_DAT  (jc10),
.ERROR  (error[7])
);

// ........

trx_path #
(
.WIDTH  (6),
.MODE   ("DDR")
)
path_ddr_6
(
.CLK    (CLK),
.RST    (RST),
.O_DAT  (data[8]),
.I_DAT  (ja10),
.ERROR  (error[8])
);

trx_path #
(
.WIDTH  (8),
.MODE   ("DDR")
)
path_ddr_8
(
.CLK    (CLK),
.RST    (RST),
.O_DAT  (data[9]),
.I_DAT  (ja9),
.ERROR  (error[9])
);

// ============================================================================
// Delay data by 1 cycle of the 100MHz clock to avoid race condition betweeen
// serialized clock and data edges. We are not using IDELAY to compensate for
// that in this design. In other words the data is delayed at the transmitter
// side.

reg [9:0] data_dly;

always @(posedge CLK100)
    data_dly <= data;

// ============================================================================
// I/O connections

reg [23:0] heartbeat_cnt;

always @(posedge CLK100)
    heartbeat_cnt <= heartbeat_cnt + 1;


assign led[9:  0] = (RST) ? 9'd0 : ~error;
assign led[   10] = heartbeat_cnt[22];
assign led[15:11] = 0;

assign jb1 = data_dly[0];
assign jb2 = data_dly[1];
assign jb3 = data_dly[2];
assign jb4 = data_dly[3];

assign jc1 = data_dly[4];
assign jc2 = data_dly[5];
assign jc3 = data_dly[6];
assign jc4 = data_dly[7];

assign ja4 = data_dly[8];
assign ja3 = data_dly[9];

assign ja1 = CLK;
assign ja2 = s_clk;

endmodule
