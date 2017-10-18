#!/bin/bash

. ../../utils/genheader.sh

vivado -mode batch -source ../generate.tcl

for x in design*.bit; do
	../../../tools/bitread -F $XRAY_ROI_FRAMES -o ${x}s -zy $x
done

for x in design_*.bits; do
	diff -u design.bits $x | grep '^[-+]bit' > ${x%.bits}.delta
done

python3 ../generate.py design_*.delta > tilegrid.json

