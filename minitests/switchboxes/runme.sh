#!/bin/bash
vivado -mode batch -source runme.tcl
../../tools/bitread -F $XRAY_ROI_FRAMES -o design.bits -zy design.bit
../../tools/bitread -F $XRAY_ROI_FRAMES -o routes.bits -zy routes.bit
