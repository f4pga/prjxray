# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
export XRAY_DATABASE="kintex7"
export XRAY_PART="xc7k160tffg676-2"
export XRAY_ROI_FRAMES="0x00000000:0xffffffff"

# All CLB's in the part, all BRAM's in the part, all DSP's in the part.
# those are site coordinats: bottom half rectangle / top half rectangle for each site type
export XRAY_ROI_TILEGRID="SLICE_X0Y0:SLICE_X109Y149 SLICE_X0Y150:SLICE_X101Y249 DSP48_X0Y0:DSP48_X5Y59 DSP48_X0Y60:DSP48_X5Y99 RAMB18_X0Y0:RAMB18_X6Y59 RAMB18_X0Y60:RAMB18_X5Y99 RAMB36_X0Y0:RAMB36_X6Y29 RAMB36_X0Y30:RAMB36_X5Y49"

export XRAY_EXCLUDE_ROI_TILEGRID=""

export XRAY_IOI3_TILES="LIOI3_X0Y9"

# These settings must remain in sync
export XRAY_ROI="SLICE_X0Y100:SLICE_X19Y149 DSP48_X0Y40:DSP48_X0Y59 RAMB18_X0Y40:RAMB18_X0Y59 RAMB36_X0Y20:RAMB36_X0Y29 IOB_X0Y100:IOB_X0Y149"
# Part of CMT X0Y1
export XRAY_ROI_GRID_X1="0"
export XRAY_ROI_GRID_X2="68"
# Include VBRK / VTERM
export XRAY_ROI_GRID_Y1="154"
export XRAY_ROI_GRID_Y2="206"

source $(dirname ${BASH_SOURCE[0]})/../utils/environment.sh

env=$(python3 ${XRAY_UTILS_DIR}/create_environment.py)
ENV_RET=$?
if [[ $ENV_RET != 0 ]] ; then
	return $ENV_RET
fi
eval $env
