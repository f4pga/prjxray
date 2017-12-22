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

if [regexp "_001$" [pwd]] {set tile [get_tiles HCLK_L_X36Y130]}
if [regexp "_002$" [pwd]] {set tile [get_tiles HCLK_R_X37Y130]}

set net [get_nets o_OBUF]
set pips [get_pips -of_objects $tile]

for {set i 0} {$i < [llength $pips]} {incr i} {
	set pip [lindex $pips $i]
	set_property IS_ROUTE_FIXED 0 $net
	route_design -unroute -net $net
	set n1 [get_nodes -uphill -of_objects $pip]
	set n2 [get_nodes -downhill -of_objects $pip]
	route_via $net "$n1 $n2"
	write_checkpoint -force design_$i.dcp
	write_bitstream -force design_$i.bit
	set fp [open "design_$i.txt" w]
	puts $fp "$tile $pip"
	close $fp
}

