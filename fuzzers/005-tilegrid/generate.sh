#!/bin/bash -x

source ${XRAY_GENHEADER}

vivado -mode batch -source ../generate.tcl

for x in design*.bit; do
	${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o ${x}s -z -y $x
done

for x in design_*.bits; do
	diff -u design.bits $x | grep '^[-+]bit' > ${x%.bits}.delta
done

python3 ../generate.py design_*.delta > tilegrid.json

