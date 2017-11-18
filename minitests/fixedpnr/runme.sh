#!/bin/bash

set -ex
vivado -mode batch -source runme.tcl
for ff in fdre fdse fdce fdpe; do
    ${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design_$ff.bits -z -y design_$ff.bit
    python3 ../../utils/segprint.py design_$ff.bits >design_$ff.seg
done
diff -u design_fdre.bits design_fdse.bits
