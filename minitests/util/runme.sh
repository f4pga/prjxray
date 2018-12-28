#!/bin/bash

set -ex
${XRAY_VIVADO} -mode batch -source $XRAY_DIR/minitests/util/runme.tcl
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design.bits -z -y design.bit
test -z "$(fgrep CRITICAL vivado.log)"
${XRAY_SEGPRINT} -z -D design.bits  >design.txt

