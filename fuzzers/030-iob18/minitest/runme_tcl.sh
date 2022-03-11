#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set -ex

: "${PROJECT:?Need to set PROJECT non-empty}"

# Create build dir
export SRC_DIR=$PWD
BUILD_DIR=build/$PROJECT
mkdir -p $BUILD_DIR
cd $BUILD_DIR

export TOP_V=$SRC_DIR/tcl.v

${XRAY_VIVADO} -mode batch -source $SRC_DIR/$PROJECT.tcl
for x in design*.bit; do
	${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o ${x}s -z -y $x
done
test -z "$(fgrep CRITICAL vivado.log)"
touch run.ok

