#!/bin/bash

set -ex
vivado -mode batch -source runme.tcl
for ff in fdre fdse fdce fdce_inv fdpe ldce ldpe; do
    ${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design_$ff.bits -z -y design_$ff.bit
    ${XRAY_SEGPRINT} -z design_$ff.bits >design_$ff.seg
done

# Clock inverter bit
diff design_fdce.seg design_fdce_inv.seg || true
# Bits set on FF's are a superset of FDPE
# FDSE has the most bits set
diff design_fdpe.seg design_fdse.seg || true
diff design_fdpe.seg design_fdce.seg || true
diff design_fdpe.seg design_fdre.seg || true

# the latch bit
diff design_fdpe.seg design_ldpe.seg || true
# LDPE has one more bit pair set than LDCE
# This is the same pair FDRE/LDCE have
diff design_ldpe.seg design_ldce.seg || true

