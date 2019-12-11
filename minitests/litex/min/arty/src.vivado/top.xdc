 ## serial:0.tx
set_property LOC D10 [get_ports serial_tx]
set_property IOSTANDARD LVCMOS33 [get_ports serial_tx]
 ## serial:0.rx
set_property LOC A9 [get_ports serial_rx]
set_property IOSTANDARD LVCMOS33 [get_ports serial_rx]
 ## cpu_reset:0
set_property LOC C2 [get_ports cpu_reset]
set_property IOSTANDARD LVCMOS33 [get_ports cpu_reset]
 ## clk100:0
set_property LOC E3 [get_ports clk100]
set_property IOSTANDARD LVCMOS33 [get_ports clk100]
 ## eth_ref_clk:0
set_property LOC G18 [get_ports eth_ref_clk]
set_property IOSTANDARD LVCMOS33 [get_ports eth_ref_clk]

set_property INTERNAL_VREF 0.675 [get_iobanks 34]

create_clock -name clk100 -period 10.0 [get_nets clk100]

set_false_path -quiet -to [get_nets -quiet -filter {mr_ff == TRUE}]

set_false_path -quiet -to [get_pins -quiet -filter {REF_PIN_NAME == PRE} -of [get_cells -quiet -filter {ars_ff1 == TRUE || ars_ff2 == TRUE}]]

set_max_delay 2 -quiet -from [get_pins -quiet -filter {REF_PIN_NAME == Q} -of [get_cells -quiet -filter {ars_ff1 == TRUE}]] -to [get_pins -quiet -filter {REF_PIN_NAME == D} -of [get_cells -quiet -filter {ars_ff2 == TRUE}]]