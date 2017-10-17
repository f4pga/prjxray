#!/bin/bash

set -ex
test $# = 1
test ! -e $1
mkdir $1
cd $1

echo '`define SEED 32'"'h$(echo $1 | md5sum | cut -c1-8)" > setseed.vh

vivado -mode batch -source ../generate.tcl

for i in 0 1 2; do
	../../../tools/bitread -F $XRAY_ROI_FRAMES -o design_$i.bits -zy design_$i.bit
	python3 ../generate.py $i
done

