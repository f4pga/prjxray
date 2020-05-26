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
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -z -y -C -o design.bits design.bit
grep -h _050_ design.bits | cut -f4 -d_ | sort | uniq -c
