#!/bin/bash

set -ex

source ${XRAY_GENHEADER}

python3 ../top.py >top.v
vivado -mode batch -source ../generate.tcl
test -z "$(fgrep CRITICAL vivado.log)"

for x in design*.bit; do
	${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o ${x}s -z -y $x
done

python3 ../generate.py

