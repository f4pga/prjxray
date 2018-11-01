#!/bin/bash

set -ex

FUZDIR=$PWD
source ${XRAY_GENHEADER}

python3 $FUZDIR/top.py >top.v
vivado -mode batch -source $FUZDIR/generate.tcl
test -z "$(fgrep CRITICAL vivado.log)"

for x in design*.bit; do
	${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o ${x}s -z -y $x
done

python3 $FUZDIR/generate.py

