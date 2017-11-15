#!/bin/bash
set -ex
vivado -mode batch -source runme.tcl
../../tools/bitread -F $XRAY_ROI_FRAMES -o design_a.bits -z -y design_a.bit
../../tools/bitread -F $XRAY_ROI_FRAMES -o design_b.bits -z -y design_b.bit
python3 ../../utils/segprint.py design_a.bits INT_L_X12Y132 INT_L_X14Y132 INT_L_X16Y132
python3 ../../utils/segprint.py design_b.bits INT_L_X12Y132 INT_L_X14Y132 INT_L_X16Y132
