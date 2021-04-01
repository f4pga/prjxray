# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
export XRAY_DATABASE="artix7"
export XRAY_PART="xc7a200tffg1156-1"
export XRAY_ROI_FRAMES="0x00000000:0xffffffff"

# All CLB's in part, all BRAM's in part, all DSP's in part.
# tcl queries IOB => don't bother adding
export XRAY_ROI_TILEGRID="SLICE_X0Y0:SLICE_X163Y249 RAMB18_X0Y0:RAMB18_X8Y99 RAMB36_X0Y0:RAMB36_X8Y49 DSP48_X0Y0:DSP48_X8Y99 IOB_X0Y0:IOB_X1Y249"

export XRAY_EXCLUDE_ROI_TILEGRID=""

# This is used by fuzzers/005-tilegrid/generate_full.py
# (special handling for frame addresses of certain IOIs -- see the script for details).
# This needs to be changed for any new device!
# If you have a FASM mismatch or unknown bits in IOIs, CHECK THIS FIRST.
export XRAY_IOI3_TILES="RIOI3_X105Y9 LIOI3_X0Y9"

source $(dirname ${BASH_SOURCE[0]})/../utils/environment.sh

env=$(python3 ${XRAY_UTILS_DIR}/create_environment.py)
ENV_RET=$?
if [[ $ENV_RET != 0 ]] ; then
	return $ENV_RET
fi
eval $env
