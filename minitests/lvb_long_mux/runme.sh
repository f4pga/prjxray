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
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design_a.bits -z -y design_a.bit
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design_b.bits -z -y design_b.bit
${XRAY_SEGPRINT} design_a.bits INT_L_X12Y132 INT_L_X14Y132 INT_L_X16Y132
${XRAY_SEGPRINT} design_b.bits INT_L_X12Y132 INT_L_X14Y132 INT_L_X16Y132
