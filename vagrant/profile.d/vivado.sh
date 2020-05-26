#!/bin/sh
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

VIVADO_BIN="$(find /opt/Xilinx/Vivado -maxdepth 2 -name bin)"
if [ -n "$VIVADO_BIN" ]; then
	export PATH=$PATH:$VIVADO_BIN
fi
