#!/bin/bash

. ../../utils/genheader.sh

echo '`define SEED 32'"'h$(echo $1 | md5sum | cut -c1-8)" > setseed.vh

vivado -mode batch -source ../generate.tcl

for x in design*.bit; do
	../../../tools/bitread -F $XRAY_ROI_FRAMES -o ${x}s -z -y $x
done

python3 ../generate.py

