create_project -force -part $::env(XRAY_PART) design design

read_verilog ../top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports i]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports o]

create_pblock roi
resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
set_param tcl.collectionResultDisplayLimit 0

place_design
route_design

write_checkpoint -force design.dcp

source ../../../utils/utils.tcl
set cells [list]

set gnd_net [create_net gnd_net]
set gnd_cell [create_cell -reference GND gnd_cell]
connect_net -net $gnd_net -objects [get_pins $gnd_cell/G]

foreach site [get_sites -of_objects [filter [roi_tiles] -filter {TYPE == "DSP_L" || TYPE == "DSP_R"}] -filter {SITE_TYPE =~ DSP*}] {
	set cell [create_cell -reference DSP48E1 ${site}_cell]
	lappend cells $cell
	set_property LOC $site $cell
	foreach pin [get_pins -of_objects $cell -filter {DIRECTION == "IN"}] {
		connect_net -net $gnd_net -objects $pin
	}
}

route_design

proc write_txtdata {filename} {
	upvar 1 cells cells
	puts "Writing $filename."
	set fp [open $filename w]
	foreach cell $cells {
		set loc [get_property LOC $cell]
		set mask [get_property MASK $cell]
		set pattern [get_property PATTERN $cell]
		set tile [get_tiles -of_objects [get_sites -filter "NAME == $loc"]]
		puts $fp "$tile $loc $mask $pattern"
	}
	close $fp
}

proc randhex {len} {
	set s ""
	for {set i 0} {$i < $len} {incr i} {
		set s "$s[format %x [expr {int(rand()*16)}]]"
	}
	return $s
}

for {set i 10} {$i < 30} {incr i} {
	foreach cell $cells {
		set_property MASK "48'h[randhex 12]" $cell
		set_property PATTERN "48'h[randhex 12]" $cell
	}
	write_checkpoint -force design_${i}.dcp
	write_bitstream -force design_${i}.bit
	write_txtdata design_${i}.txt
}

