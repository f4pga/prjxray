# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
# XC7A35T-1CPG236C

source $(dirname ${BASH_SOURCE[0]})/../../settings/artix7_50t.sh

export XRAY_PART=xc7a35tcpg236-1

if [ -z "$XRAY_PINCFG" ]; then
	echo "XRAY_PINCFG not set"
	return 1
fi
if [ -z "$XRAY_DIN_N_LARGE" ]; then
	echo "XRAY_DIN_N_LARGE not set"
	return 1
fi
if [ -z "$XRAY_DOUT_N_LARGE" ]; then
	echo "XRAY_DOUT_N_LARGE not set"
	return 1
fi

# ROI is in the top left
export XRAY_ROI_LARGE=SLICE_X0Y100:SLICE_X35Y149

# HCLK Tile
export XRAY_ROI_HCLK="CLK_HROW_TOP_R_X60Y130/CLK_HROW_CK_BUFHCLK_L0"

# PITCH
export XRAY_PITCH=2

# INT_L/R for DOUT and DIN
export XRAY_ROI_DIN_INT_L_X="0"
export XRAY_ROI_DIN_INT_R_X="25"
export XRAY_ROI_DOUT_INT_L_X="2"
export XRAY_ROI_DOUT_INT_R_X="23"

# PIPS for DOUT and DIN
export XRAY_ROI_DIN_LPIP="EE2BEG2"
export XRAY_ROI_DIN_RPIP="WW2BEG1"
export XRAY_ROI_DOUT_LPIP="SW6BEG0"
export XRAY_ROI_DOUT_RPIP="LH12"

source $XRAY_DIR/utils/environment.sh
