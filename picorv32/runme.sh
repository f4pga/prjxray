#!/bin/bash

set -ex

source ../settings.sh

cat > design.xdc << EOT
set_property -dict {PACKAGE_PIN $XRAY_PIN_00 IOSTANDARD LVCMOS33} [get_ports clk]
set_property -dict {PACKAGE_PIN $XRAY_PIN_01 IOSTANDARD LVCMOS33} [get_ports din]
set_property -dict {PACKAGE_PIN $XRAY_PIN_02 IOSTANDARD LVCMOS33} [get_ports dout]
set_property -dict {PACKAGE_PIN $XRAY_PIN_03 IOSTANDARD LVCMOS33} [get_ports stb]

set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A5 I5:A6} \
		[get_cells -quiet -filter {REF_NAME == LUT6} -hierarchical]

create_pblock roi
add_cells_to_pblock [get_pblocks roi] [get_cells -quiet [list picorv32]]
resize_pblock [get_pblocks roi] -add {$XRAY_ROI}

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]
EOT

cat > design.tcl << EOT
create_project -force -part $XRAY_PART design design

read_xdc design.xdc
read_verilog design.v
read_verilog picorv32.v

synth_design -top top
place_design
route_design

write_checkpoint -force design.dcp
write_bitstream -force design.bit

puts "Writing lutlist.txt."
current_instance picorv32
set fp [open "lutlist.txt" w]
set luts [get_cells -filter {REF_NAME == LUT6}]
foreach lut $luts {
	set bel [get_property BEL $lut]
	set loc [get_property LOC $lut]
	set init [get_property INIT $lut]
	puts $fp "$loc $bel $init"
}
close $fp
EOT

rm -rf design design.log
vivado -nojournal -log design.log -mode batch -source design.tcl
../tools/bitread -o design.bits -zy < design.bit

