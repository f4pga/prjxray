#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

source ${XRAY_GENHEADER}

${XRAY_VIVADO} -mode batch -source $FUZDIR/generate.tcl

for x in design_*.bit; do
	${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o ${x}s -z -y ${x}
done

python3 $FUZDIR/generate.py $(ls design_*.bit | cut -f1 -d.)

