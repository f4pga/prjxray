#!/bin/bash

set -ex
vivado -mode batch -source runme.tcl

${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design.bits -z -y design.bit
${XRAY_SEGPRINT} -bzd design.bits > design.segs

for id in b{0,1,2,3,4,5,6,7,8,9,10,11}; do
	${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design_$id.bits -z -y design_$id.bit
	${XRAY_SEGPRINT} -bzd design_$id.bits > design_$id.segs
done
