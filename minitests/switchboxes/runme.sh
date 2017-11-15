#!/bin/bash

vivado -mode batch -source runme.tcl
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design.bits -z -y design.bit
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o routes.bits -z -y routes.bit
${XRAY_SEGPRINT} routes.bits INT_L_X12Y119 INT_L_X12Y117 INT_L_X12Y115
${XRAY_SEGPRINT} routes.bits INT_R_X13Y118 INT_R_X13Y116 INT_R_X13Y114
