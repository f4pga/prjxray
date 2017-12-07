#!/bin/bash

set -ex
yosys run_yosys.ys
vivado -mode batch -source runme.tcl
test -z $(fgrep CRITICAL vivado.log)
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design.bits -z -y design.bit
${XRAY_SEGPRINT} -z -D design.bits  >design.txt
# test -z $(cat design.txt)
test $(wc -c design.txt  |cut -d\  -f 1) = 0

