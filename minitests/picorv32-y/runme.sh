#!/bin/bash

set -ex
yosys run_yosys.ys
${XRAY_VIVADO} -mode batch -source runme.tcl
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design.bits -z -y design.bit
test -z "$(fgrep CRITICAL vivado.log)"
${XRAY_SEGPRINT} -z -D design.bits  >design.txt

# All bits solved?
test $(wc -c design.txt  |cut -d\  -f 1) = 0

