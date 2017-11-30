#!/bin/bash

source ${XRAY_GENHEADER}

vivado -mode batch -source ../generate.tcl

for x in design_*.bit; do
	${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o ${x}s -z -y ${x}
done

python3 ../generate.py $(ls design_*.bit | cut -f1 -d.)

