export XRAY_DATABASE="zynq7"
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
export XRAY_PART="xc7z010clg400-1"
export XRAY_ROI_FRAMES="0x00000000:0xffffffff"

# All CLB's in part, all BRAM's in part, all DSP's in part.
export XRAY_ROI_TILEGRID="SLICE_X0Y0:SLICE_X43Y99 RAMB18_X0Y0:RAMB18_X2Y39 RAMB36_X0Y0:RAMB36_X2Y19 DSP48_X0Y0:DSP48_X1Y39"

export XRAY_EXCLUDE_ROI_TILEGRID=""

export XRAY_IOI3_TILES="RIOI3_X31Y9"
export XRAY_PS7_INT="INT_L_X0Y50"

# These settings must remain in sync
export XRAY_ROI="SLICE_X00Y50:SLICE_X43Y99 RAMB18_X0Y20:RAMB18_X2Y39 RAMB36_X0Y10:RAMB36_X2Y19 IOB_X0Y50:IOB_X0Y99"

# Most of CMT X0Y2.
export XRAY_ROI_GRID_X1="83"
export XRAY_ROI_GRID_X2="118"
# Include VBRK / VTERM
export XRAY_ROI_GRID_Y1="0"
export XRAY_ROI_GRID_Y2="51"

source $(dirname ${BASH_SOURCE[0]})/../utils/environment.sh

env=$(python3 ${XRAY_UTILS_DIR}/create_environment.py)
ENV_RET=$?
if [[ $ENV_RET != 0 ]] ; then
	return $ENV_RET
fi
eval $env
