#!/bin/bash

set -ex
vivado -mode batch -source runme.tcl
for bit in $(ls *.bit); do
    ${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o ${bit}s -z -y $bit
done

for b in $(ls *.bits); do
    echo
    echo $b
    diff design_ref.bits $b |grep '[<>]' |sed 's/^/  /'
done
