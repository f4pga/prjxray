#!/bin/bash

set -ex
vivado -mode batch -source runme.tcl
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design_fdre.bits -z -y design_fdre.bit
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design_fdse.bits -z -y design_fdse.bit
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design_fdce.bits -z -y design_fdce.bit
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design_fdpe.bits -z -y design_fdpe.bit
diff -u design_fdre.bits design_fdse.bits
