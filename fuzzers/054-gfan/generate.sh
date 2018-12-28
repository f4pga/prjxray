#!/bin/bash

echo "test: $PWD"
FUZDIR=$PWD
source ${XRAY_GENHEADER}

${XRAY_VIVADO} -mode batch -source ../generate.tcl

${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design.bits -z -y design.bit
python3 ../generate.py

