#!/bin/bash

set -ex
rm -f out_last
vivado -mode batch -source runme.tcl
test -z "$(fgrep CRITICAL vivado.log)"

pushd out_last
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design.bits -z -y design.bit
${XRAY_SEGPRINT} -zd design.bits >design.segp
${XRAY_DIR}/tools/segprint2fasm.py design.segp design.fasm
${XRAY_DIR}/tools/fasm2frame.py design.fasm design.frm
popd
