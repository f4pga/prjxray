create_project -force -part $::env(XRAY_PART) design design

read_verilog ../top.v
read_verilog ../picorv32.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports din]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports dout]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports stb]

create_pblock roi
add_cells_to_pblock [get_pblocks roi] [get_cells roi]
resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]

source ../../../utils/utils.tcl
randplace_pblock 100 roi

place_design
route_design

write_checkpoint -force design.dcp

proc write_txtdata {filename} {
	puts "Writing $filename."
	set fp [open $filename w]
	foreach tile [get_tiles [regsub -all {CLBL[LM]} [get_tiles -of_objects [get_sites -of_objects [get_pblocks roi]]] INT]] {
		puts "Dumping pips from tile $tile"
		foreach pip [get_pips -filter {IS_DIRECTIONAL} -of_objects $tile] {
			if {[get_nets -quiet -of_objects $pip] != {}} {
				set src_wire [get_wires -uphill -of_objects $pip]
				set dst_wire [get_wires -downhill -of_objects $pip]
				if {[llength [get_nodes -uphill -of_objects [get_nodes -of_objects $dst_wire]]] != 1} {
					puts $fp "$tile $pip $src_wire $dst_wire"
				}
			}
		}
	}
	close $fp
}

write_bitstream -force design.bit
write_txtdata design.txt

