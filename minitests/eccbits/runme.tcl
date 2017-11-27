create_project -force -part $::env(XRAY_PART) design design

read_verilog top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports a]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports y]

create_pblock roi
resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

source ../../utils/utils.tcl

proc get_rand_lut6_init {} {
	return "64'h[format %08x [expr int(rand() * 65536 * 65536)]][format %08x [expr int(rand() * 65536 * 65536)]]"
}

set i 1
foreach site [randsample_list 100 [get_sites -of_objects [get_pblocks roi]]] {
	puts "$i/100: $site"
	incr i

	create_cell -reference LUT6 LUT_${site}_ALUT
	create_cell -reference LUT6 LUT_${site}_BLUT
	create_cell -reference LUT6 LUT_${site}_CLUT
	create_cell -reference LUT6 LUT_${site}_DLUT

	set_property -dict "LOC $site BEL A6LUT INIT [get_rand_lut6_init]" [get_cells LUT_${site}_ALUT]
	set_property -dict "LOC $site BEL B6LUT INIT [get_rand_lut6_init]" [get_cells LUT_${site}_BLUT]
	set_property -dict "LOC $site BEL C6LUT INIT [get_rand_lut6_init]" [get_cells LUT_${site}_CLUT]
	set_property -dict "LOC $site BEL D6LUT INIT [get_rand_lut6_init]" [get_cells LUT_${site}_DLUT]

	connect_net -net [get_nets y_OBUF] -objects [get_pins "
		LUT_${site}_ALUT/I0 LUT_${site}_ALUT/I1 LUT_${site}_ALUT/I2 LUT_${site}_ALUT/I3 LUT_${site}_ALUT/I4 LUT_${site}_ALUT/I5
		LUT_${site}_BLUT/I0 LUT_${site}_BLUT/I1 LUT_${site}_BLUT/I2 LUT_${site}_BLUT/I3 LUT_${site}_BLUT/I4 LUT_${site}_BLUT/I5
		LUT_${site}_CLUT/I0 LUT_${site}_CLUT/I1 LUT_${site}_CLUT/I2 LUT_${site}_CLUT/I3 LUT_${site}_CLUT/I4 LUT_${site}_CLUT/I5
		LUT_${site}_DLUT/I0 LUT_${site}_DLUT/I1 LUT_${site}_DLUT/I2 LUT_${site}_DLUT/I3 LUT_${site}_DLUT/I4 LUT_${site}_DLUT/I5
	"]
}

place_design
route_design

write_checkpoint -force design.dcp
write_bitstream -force design.bit

