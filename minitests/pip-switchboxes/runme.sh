#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

${XRAY_VIVADO} -mode batch -source runme.tcl
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design.bits -z -y design.bit
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o routes.bits -z -y routes.bit
${XRAY_SEGPRINT} routes.bits INT_L_X12Y119 INT_L_X12Y117 INT_L_X12Y115
${XRAY_SEGPRINT} routes.bits INT_R_X13Y118 INT_R_X13Y116 INT_R_X13Y114
