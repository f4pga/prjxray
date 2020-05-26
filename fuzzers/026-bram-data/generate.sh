#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set -ex

FUZDIR=$PWD
source ${XRAY_GENHEADER}

python3 $FUZDIR/top.py >top.v
${XRAY_VIVADO} -mode batch -source $FUZDIR/generate.tcl
test -z "$(fgrep CRITICAL vivado.log)"

for x in design*.bit; do
	${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o ${x}s -z -y $x
done

python3 $FUZDIR/generate.py

