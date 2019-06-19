#!/bin/bash

set -ex

# Create build dir
export SRC_DIR=$PWD
export BUILD_DIR=build

mkdir -p $BUILD_DIR
cd $BUILD_DIR

${XRAY_VIVADO} -mode batch -source $SRC_DIR/runme.tcl
test -z "$(fgrep CRITICAL vivado.log)" && touch run.ok
