#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set -ex
${XRAY_VIVADO} -mode batch -source runme.tcl

${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design.bits -z -y design.bit
${XRAY_SEGPRINT} -bzd design.bits > design.segs

for id in b{0,1,2,3,4,5,6,7,8,9,10,11}; do
	${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design_$id.bits -z -y design_$id.bit
	${XRAY_SEGPRINT} -bzd design_$id.bits > design_$id.segs
done
