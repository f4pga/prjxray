#!/bin/bash

set -ex
source nexys_video.sh

rm -rf build
mkdir build
cd build
${XRAY_VIVADO} -mode batch -source ../runme.tcl
python3 ${XRAY_DIR}/utils/bit2fasm.py --verbose design.bit > design.fasm

