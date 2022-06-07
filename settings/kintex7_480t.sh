# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
export XRAY_DATABASE="kintex7"
export XRAY_PART="xc7k480tffg1156-2"
export XRAY_ROI_FRAMES="0x00000000:0xffffffff"

export XRAY_PIN_00=AL18
export XRAY_PIN_01=AL19
export XRAY_PIN_02=AK18
export XRAY_PIN_03=AK19

# All CLB's in part, all BRAM's in part, all DSP's in part.
# tcl queries IOB => don't bother adding
export XRAY_ROI_TILEGRID="SLICE_X0Y0:SLICE_X153Y349 DSP48_X0Y0:DSP48_X5Y139 RAMB18_X0Y0:RAMB18_X5Y139 RAMB36_X0Y0:RAMB36_X4Y69"

export XRAY_EXCLUDE_ROI_TILEGRID=""

# This is used by fuzzers/005-tilegrid/generate_full.py
# (special handling for frame addresses of certain IOIs -- see the script for details).
# This needs to be changed for any new device!
# If you have a FASM mismatch or unknown bits in IOIs, CHECK THIS FIRST.
export XRAY_IOI3_TILES=""

# These settings must remain in sync
export XRAY_ROI="SLICE_X0Y0:SLICE_X153Y349 DSP48_X0Y0:DSP48_X5Y139 RAMB18_X0Y0:RAMB18_X5Y139 RAMB36_X0Y0:RAMB36_X4Y69"
# Part of CMT X0Y1
export XRAY_ROI_GRID_X1="-1"
export XRAY_ROI_GRID_X2="-1"
# Include VBRK / VTERM
export XRAY_ROI_GRID_Y1="-1"
export XRAY_ROI_GRID_Y2="-1"

source $(dirname ${BASH_SOURCE[0]})/../utils/environment.sh

env=$(python3 ${XRAY_UTILS_DIR}/create_environment.py)
ENV_RET=$?
if [[ $ENV_RET != 0 ]] ; then
        return $ENV_RET
fi
eval $env
