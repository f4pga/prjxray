create_project -force -part $::env(XRAY_PART) design design

read_verilog ../top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports rst]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports di]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports do]

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


########################################
# Unmodified design with random LUTs

proc write_txtdata {filename} {
	puts "Writing $filename."
	set fp [open $filename w]
	foreach cell [get_cells -hierarchical -filter {REF_NAME == FDRE || REF_NAME == FDSE || REF_NAME == FDCE || REF_NAME == FDPE}] {
		set loc [get_property LOC $cell]
		set bel [get_property BEL $cell]
		set ctype [get_property REF_NAME $cell]
		set init [get_property INIT $cell]
		set cinv [get_property IS_C_INVERTED $cell]
		puts $fp "$loc $bel $ctype $init $cinv"
	}
	close $fp
}

write_bitstream -force design_0.bit
write_txtdata design_0.txt


########################################
# Versions with random config changes

proc change_design_randomly {} {
	foreach cell [get_cells -hierarchical -filter {REF_NAME == FDRE}] {
		set site_cells [get_cells -of_objects [get_sites -of_objects $cell] -filter {REF_NAME == FDRE || REF_NAME == FDSE || REF_NAME == FDCE || REF_NAME == FDPE}]
		set_property INIT 1'b[expr int(rand()*2)] $cell
		set_property IS_C_INVERTED 1'b[expr int(rand()*2)] $site_cells
	}
}

for {set i 1} {$i < 10} {incr i} {
	change_design_randomly
	write_bitstream -force design_$i.bit
	write_txtdata design_$i.txt
}

