#!/bin/bash

. ../../utils/genheader.sh

vivado -mode batch -source ../generate.tcl

for i in {0..9}; do
	../../../tools/bitread -F $XRAY_ROI_FRAMES -o design_$i.bits -zy design_$i.bit
	python3 ../generate.py $i
done

