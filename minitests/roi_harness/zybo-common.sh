# XC7010-1CLG400C
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
export XRAY_PART=xc7z010clg400-1

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

# ROI is in top right
export XRAY_ROI_LARGE="SLICE_X22Y50:SLICE_X43Y99"

# HCLK Tile
export XRAY_ROI_HCLK="CLK_HROW_TOP_R_X82Y78/CLK_HROW_CK_BUFHCLK_R0"

# PITCH
export XRAY_PITCH=3

# INT_L/R for DOUT and DIN
export XRAY_ROI_DIN_INT_L_X=
export XRAY_ROI_DIN_INT_R_X="31"
export XRAY_ROI_DOUT_INT_L_X=
export XRAY_ROI_DOUT_INT_R_X="29"

# PIPS for DOUT and DIN
export XRAY_ROI_DIN_LPIP=
export XRAY_ROI_DIN_RPIP="WW2BEG1"
export XRAY_ROI_DOUT_LPIP=
export XRAY_ROI_DOUT_RPIP="EE2BEG0"

source $XRAY_DIR/utils/environment.sh
