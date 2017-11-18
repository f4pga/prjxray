#!/bin/bash

source ${XRAY_GENHEADER}

vivado -mode batch -source ../generate.tcl

for x in design_[0-9][0-9][0-9].bit; do
	${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o ${x}s -z -y $x
done

python3 ../generate.py design_[0-9][0-9][0-9].bit

