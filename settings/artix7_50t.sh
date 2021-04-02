# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
export XRAY_DATABASE="artix7"
export XRAY_PART="xc7a50tfgg484-1"
export XRAY_ROI_FRAMES="0x00000000:0xffffffff"

# All CLB's in part, all BRAM's in part, all DSP's in part.
# tcl queries IOB => don't bother adding
export XRAY_ROI_TILEGRID="SLICE_X0Y0:SLICE_X65Y99 SLICE_X0Y100:SLICE_X57Y149 RAMB18_X0Y0:RAMB18_X1Y59 RAMB36_X0Y0:RAMB36_X1Y29 RAMB18_X2Y0:RAMB18_X2Y39 RAMB36_X2Y0:RAMB36_X2Y19 DSP48_X0Y0:DSP48_X1Y59"

export XRAY_EXCLUDE_ROI_TILEGRID=""

# This is used by fuzzers/005-tilegrid/generate_full.py
# (special handling for frame addresses of certain IOIs -- see the script for details).
# This needs to be changed for any new device!
# If you have a FASM mismatch or unknown bits in IOIs, CHECK THIS FIRST.
export XRAY_IOI3_TILES="LIOI3_X0Y9 RIOI3_X43Y9"

# These settings must remain in sync
export XRAY_ROI="SLICE_X0Y100:SLICE_X35Y149 RAMB18_X0Y40:RAMB18_X0Y59 RAMB36_X0Y20:RAMB36_X0Y29 DSP48_X0Y40:DSP48_X0Y59 IOB_X0Y100:IOB_X0Y149"
# Most of CMT X0Y2.
export XRAY_ROI_GRID_X1="10"
export XRAY_ROI_GRID_X2="58"
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
