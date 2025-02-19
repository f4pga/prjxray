# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

source "$::env(XRAY_DIR)/utils/utils.tcl"

create_project -force -name design -part $::env(XRAY_PART)
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

dump_pins $::env(FILE_NAME) GTXE2_CHANNEL
