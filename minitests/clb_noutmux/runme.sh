#!/bin/bash

set -ex
# rm -f vivado*.log vivado*.jou
vivado -mode batch -source runme.tcl
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design.bits -z -y design.bit
#${XRAY_SEGPRINT} design.bits SLICE_X16Y100 SLICE_X16Y101 SLICE_X16Y102 SLICE_X16Y103
