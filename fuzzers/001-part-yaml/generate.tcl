create_project -force -part $::env(XRAY_PART) design design

read_verilog ../top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports di]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports do]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports stb]

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_param tcl.collectionResultDisplayLimit 0

set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]

if { ![info exists ::env(XRAY_XC7Z)] } {
	# Place and Route
	place_design
	route_design

	write_checkpoint -force design.dcp

	# Write a normal bitstream that will do a singe FDRI write of all the frames.
	write_bitstream -force design.bit

	# Write a debug bitstream which writes each frame individually followed by
	# the frame address.  This shows where there are gaps in the frame address
	# space.
	set_property BITSTREAM.GENERAL.DEBUGBITSTREAM YES [current_design]
	write_bitstream -force design.debug.bit
	set_property BITSTREAM.GENERAL.DEBUGBITSTREAM NO [current_design]

	set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
	write_bitstream -force design.perframecrc.bit
	set_property BITSTREAM.GENERAL.PERFRAMECRC NO [current_design]
} else {
	# Create and launch synthesis and implementation runs
	launch_runs synth_1 -jobs 6
	wait_on_run synth_1
	launch_runs impl_1
	wait_on_run impl_1

	place_design
	route_design

	write_checkpoint -force design.dcp

	write_bitstream -force design.bit

	open_run impl_1

	### Creating configuration file to be parsed by python script

	# Getting the number of rows on the device
	set count 0
	set rows [get_clock_regions -regexp -filter {NAME =~ "X0Y.*"}]
	foreach row $rows {incr count}

	# Getting the BUFG_CLK_TOP position
	set bufg [get_tiles -regexp -filter {NAME =~ "CLK_BUFG_TOP.*?([0-9]+)$"}]

	# Writing to file
	set fp [open "device.cfg" "w"]
	puts $fp $count
	puts $fp $bufg
	close $fp

	for {set i 0} {$i < $count} {incr i} {
		set fp [open "row_$i.cfg" "w"]
		set yval [expr $i * 50]
		set tiles [get_tiles -of_objects [get_clock_regions] -regexp -filter [format {NAME =~ "((CLB.*Y)|((L|R)IOI.*Y)|(BRAM_(L|R).*Y)|(DSP.*Y))%s"} $yval]]
		puts $fp $tiles
		close $fp
	}
}
