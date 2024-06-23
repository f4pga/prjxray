# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
export XRAY_DATABASE="kintex7"
export XRAY_PART="xc7k410tfbg900-1"
export XRAY_ROI_FRAMES="0x00000000:0xffffffff" 

export XRAY_ROI_TILEGRID="SLICE_X0Y0:SLICE_X189Y149 SLICE_X0Y150:SLICE_X181Y349 RAMB18_X0Y0:RAMB18_X11Y59 RAMB18_X0Y60:RAMB18_X10Y139 RAMB36_X0Y0:RAMB36_X11Y29 RAMB36_X0Y30:RAMB36_X10Y69 DSP48_X0Y0:DSP48_X10Y59 DSP48_X0Y60:DSP48_X10Y139"

export XRAY_EXCLUDE_ROI_TILEGRID=""

export XRAY_IOI3_TILES="LIOI3_X0Y9"

export XRAY_ROI="SLICE_X0Y50:SLICE_X99Y99 DSP48_X0Y20:DSP48_X0Y39 RAMB18_X0Y20:RAMB18_X0Y39 RAMB36_X0Y10:RAMB36_X0Y19 IOB_X0Y50:IOB_X0Y99"
# CMT X0Y1
export XRAY_ROI_GRID_X1="0"
export XRAY_ROI_GRID_X2="165"
# Include VBRK / VTERM
export XRAY_ROI_GRID_Y1="260"
export XRAY_ROI_GRID_Y2="312"

source $(dirname ${BASH_SOURCE[0]})/../utils/environment.sh

env=$(python3 ${XRAY_UTILS_DIR}/create_environment.py)
ENV_RET=$?
if [[ $ENV_RET != 0 ]] ; then
	return $ENV_RET
fi
eval $env
