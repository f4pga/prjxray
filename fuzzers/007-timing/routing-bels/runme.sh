#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set -ex

# Create build dir
export SRC_DIR=$PWD
export BUILD_DIR=build

mkdir -p $BUILD_DIR
cd $BUILD_DIR

${XRAY_VIVADO} -mode batch -source $SRC_DIR/runme.tcl
test -z "$(fgrep CRITICAL vivado.log)" && touch run.ok
