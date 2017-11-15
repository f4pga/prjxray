#!/bin/bash

source ../../utils/environment.sh

set -ex
test $# = 1
test ! -e $1
mkdir $1
cd $1

cat > design.xdc << EOT
set_property -dict {PACKAGE_PIN $XRAY_PIN_00 IOSTANDARD LVCMOS33} [get_ports clk]
set_property -dict {PACKAGE_PIN $XRAY_PIN_01 IOSTANDARD LVCMOS33} [get_ports din]
set_property -dict {PACKAGE_PIN $XRAY_PIN_02 IOSTANDARD LVCMOS33} [get_ports dout]
set_property -dict {PACKAGE_PIN $XRAY_PIN_03 IOSTANDARD LVCMOS33} [get_ports stb]

set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A5 I5:A6} \
		[get_cells -quiet -filter {REF_NAME == LUT6} -hierarchical]

create_pblock roi
add_cells_to_pblock [get_pblocks roi] [get_cells stuff]
resize_pblock [get_pblocks roi] -add {$XRAY_ROI}

# requires partial reconfiguration license
#set_property HD.RECONFIGURABLE TRUE [get_cells stuff]

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]
EOT

echo '`define SEED 32'"'h$(echo $1 | md5sum | cut -c1-8)" > setseed.vh

cat > design.tcl << EOT
source "../utilities.tcl"
create_project -force -part $XRAY_PART design design

read_xdc design.xdc
read_verilog ../design.v
read_verilog ../picorv32.v

synth_design -top top
place_design
route_design

write_checkpoint -force design.dcp
write_bitstream -force design.bit

puts "Writing lutdata.txt."
set fp [open "lutdata.txt" w]
foreach cell [get_cells -hierarchical -filter {REF_NAME == LUT6}] {
	set bel [get_property BEL \$cell]
	set loc [get_property LOC \$cell]
	set init [get_property INIT \$cell]
	puts \$fp "\$loc \$bel \$init"
}
close \$fp

puts "Writing carrydata.txt."
set fp [open "carrydata.txt" w]
foreach cell [get_cells -hierarchical -filter {REF_NAME == CARRY4}] {
	set loc [get_property LOC \$cell]
	set cyinit_mux [get_carry_cyinit_mux_cfg \$cell]
	set di0_mux [get_carry_di0_mux_cfg \$cell]
	set di1_mux [get_carry_di1_mux_cfg \$cell]
	set di2_mux [get_carry_di2_mux_cfg \$cell]
	set di3_mux [get_carry_di3_mux_cfg \$cell]
	puts \$fp "\$loc \$cyinit_mux \$di0_mux \$di1_mux \$di2_mux \$di3_mux"
}
close \$fp
EOT

rm -rf design design.log
vivado -nojournal -log design.log -mode batch -source design.tcl

#${XRAY_BITREAD} -o design_roi.bits -z -y design_roi_partial.bit
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design.bits -z -y design.bit
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design.pgm -p design.bit

python3 ../segdata.py
#${XRAY_SEGMATCH} < segdata.txt > database.txt

