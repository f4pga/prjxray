#!/bin/bash

. ../../utils/genheader.sh

echo '`define SEED 32'"'h$(echo $1 | md5sum | cut -c1-8)" > setseed.vh

vivado -mode batch -source ../generate.tcl

../../../tools/bitread -F $XRAY_ROI_FRAMES -o design.bits -zy design.bit
python3 ../generate.py

