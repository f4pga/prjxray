#!/bin/bash

source ${XRAY_GENHEADER}

while ! vivado -mode batch -source ../generate.tcl; do
	rm -rf design*
done

${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design.bits -z -y design.bit
python3 ../generate.py

