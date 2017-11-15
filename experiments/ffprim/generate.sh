#!/bin/bash

set -ex

. ../../utils/genheader.sh

#echo '`define SEED 32'"'h$(echo $1 | md5sum | cut -c1-8)" > setseed.vh

python3 ../top.py >top.v
vivado -mode batch -source ../generate.tcl

for x in design*.bit; do
	../../../tools/bitread -F $XRAY_ROI_FRAMES -o ${x}s -zy $x
done

python3 ../generate.py

