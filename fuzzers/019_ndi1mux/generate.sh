#!/bin/bash

set -ex

source ${XRAY_GENHEADER}

#echo '`define SEED 32'"'h$(echo $1 | md5sum | cut -c1-8)" > setseed.vh

python3 ../top.py >top.v
vivado -mode batch -source ../generate.tcl
test -z "$(fgrep CRITICAL vivado.log)"

for x in design*.bit; do
	${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o ${x}s -z -y $x
done

python3 ../generate.py

