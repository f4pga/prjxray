#!/bin/bash
set -ex
vivado -mode batch -source runme.tcl
../../tools/bitread -F $XRAY_ROI_FRAMES -o design.bits -z -y design.bit
python3 ../../utils/segprint.py design.bits SLICE_X16Y100 SLICE_X16Y101 SLICE_X16Y102 SLICE_X16Y103
