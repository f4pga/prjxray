#!/bin/bash

set -ex

: "${PROJECT:?Need to set PROJECT non-empty}"

# Create build dir
export SRC_DIR=$PWD
export BUILD_DIR=build/$PROJECT
mkdir -p $BUILD_DIR
cd $BUILD_DIR
python3 ${SRC_DIR}/top.py > top.v

${XRAY_VIVADO} -mode batch -source $SRC_DIR/generate.tcl
for x in design*.bit; do
	${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o ${x}s -z -y $x
done
test -z "$(fgrep CRITICAL vivado.log)" && touch run.ok
python3 ${SRC_DIR}/compare.py
