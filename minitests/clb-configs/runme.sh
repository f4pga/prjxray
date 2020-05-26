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
${XRAY_SEGPRINT} design.bits SLICE_X16Y100 SLICE_X16Y101 SLICE_X16Y102 SLICE_X16Y103
