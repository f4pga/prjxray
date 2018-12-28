#!/bin/bash

set -ex
${XRAY_VIVADO} -mode batch -source runme.tcl
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -z -y -C -o design.bits design.bit
grep -h _050_ design.bits | cut -f4 -d_ | sort | uniq -c
