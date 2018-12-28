#!/bin/bash

set -ex

: "${PROJECT:?Need to set PROJECT non-empty}"

# Create build dir
export SRC_DIR=$PWD
BUILD_DIR=build/$PROJECT
mkdir -p $BUILD_DIR
cd $BUILD_DIR

export TOP_V=$SRC_DIR/top.v

${XRAY_VIVADO} -mode batch -source $SRC_DIR/runme.tcl
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design.bits -z -y design.bit
test -z "$(fgrep CRITICAL vivado.log)"

