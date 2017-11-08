create_project -force -part $::env(XRAY_PART) design design

read_verilog ../top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports di]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports do]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports stb]

set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A5 I5:A6} \
		[get_cells -quiet -filter {REF_NAME == LUT6} -hierarchical]

create_pblock roi
add_cells_to_pblock [get_pblocks roi] [get_cells roi]
resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]

place_design
route_design

write_checkpoint -force design.dcp

proc write_txtdata {filename} {
	puts "Writing $filename."
	set fp [open $filename w]
	foreach tile [get_tiles -of_objects [get_sites -of_objects [get_pblocks roi]]] {
		puts "Dumping pips from tile $tile"
		foreach pip [get_pips -of_objects $tile] {
			if {[get_nets -quiet -of_objects $pip] == {}} {puts $fp "$pip 0"} {puts $fp "$pip 1"}
		}
	}
	close $fp
}

write_bitstream -force design.bit
write_txtdata design.txt

