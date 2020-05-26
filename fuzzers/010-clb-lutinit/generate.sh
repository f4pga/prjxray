#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

FUZDIR=$PWD
source ${XRAY_GENHEADER}

echo '`define SEED 32'"'h$(echo $1 | md5sum | cut -c1-8)" > setseed.vh

${XRAY_VIVADO} -mode batch -source $FUZDIR/generate.tcl

for i in 0 1 2; do
	${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design_$i.bits -z -y design_$i.bit
done

for i in 0 1 2; do
	python3 $FUZDIR/generate.py $i
done

