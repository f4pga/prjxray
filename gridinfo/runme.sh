#!/bin/bash

set -ex

cat > design.xdc << EOT
set_property -dict {PACKAGE_PIN $XRAY_PIN_00 IOSTANDARD LVCMOS33} [get_ports I[0]]
set_property -dict {PACKAGE_PIN $XRAY_PIN_01 IOSTANDARD LVCMOS33} [get_ports I[1]]
set_property -dict {PACKAGE_PIN $XRAY_PIN_02 IOSTANDARD LVCMOS33} [get_ports I[2]]
set_property -dict {PACKAGE_PIN $XRAY_PIN_03 IOSTANDARD LVCMOS33} [get_ports I[3]]
set_property -dict {PACKAGE_PIN $XRAY_PIN_04 IOSTANDARD LVCMOS33} [get_ports I[4]]
set_property -dict {PACKAGE_PIN $XRAY_PIN_05 IOSTANDARD LVCMOS33} [get_ports I[5]]
set_property -dict {PACKAGE_PIN $XRAY_PIN_06 IOSTANDARD LVCMOS33} [get_ports O]

set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A5 I5:A6} [get_cells lut]
set_property -dict {IS_LOC_FIXED 1 IS_BEL_FIXED 1 BEL SLICEL.A6LUT} [get_cells lut]

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
EOT

cat > design.v << EOT
module top(input [5:0] I, output O);
	LUT6 #(.INIT(64'h8000000000000000)) lut (
		.I0(I[0]), 
		.I1(I[1]), 
		.I2(I[2]), 
		.I3(I[3]), 
		.I4(I[4]), 
		.I5(I[5]), 
		.O(O)
	);
endmodule
EOT

cat > design.tcl << EOT
create_project -force -part $XRAY_PART design design

read_xdc design.xdc
read_verilog design.v

synth_design -top top
place_design
route_design

write_checkpoint -force design.dcp

source logicframes.tcl
source tiledata.tcl
EOT

rm -f design.log
vivado -nojournal -log design.log -mode batch -source design.tcl

{
	sed -e '/^--tiledata--/ { s/[^ ]* //; p; }; d;' design.log

	for f0 in logicframes_SLICE_*_0.bit; do
		f1=${f0%_0.bit}_1.bit
		${XRAY_BITREAD} -x -o ${f0%.bit}.asc $f0 > /dev/null
		${XRAY_BITREAD} -x -o ${f1%.bit}.asc $f1 > /dev/null
		f0=${f0%.bit}.asc
		f1=${f1%.bit}.asc
		n=${f0%_0.asc}
		n=${n#logicframes_}
		echo SLICEBIT $n $( diff $f0 $f1 | grep '^>' | cut -c3-; )
	done
} > grid-${XRAY_PART}-db.txt

python3 gridinfo-txt2json.py grid-${XRAY_PART}-db ${XRAY_PART}

