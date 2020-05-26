#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set -ex
yosys run_yosys.ys
${XRAY_VIVADO} -mode batch -source runme.tcl
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design.bits -z -y design.bit
test -z "$(fgrep CRITICAL vivado.log)"
${XRAY_SEGPRINT} -z -D design.bits  >design.txt

# All bits solved?
test $(wc -c design.txt  |cut -d\  -f 1) = 0

