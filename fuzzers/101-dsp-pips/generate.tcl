# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
source "$::env(XRAY_DIR)/utils/utils.tcl"

proc run {} {
    create_project -force -part $::env(XRAY_PART) design design
    read_verilog top.v
    synth_design -top top

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

    set_property IS_ENABLED 0 [get_drc_checks {DSPS-1}]
    set_property IS_ENABLED 0 [get_drc_checks {DSPS-3}]
    set_property IS_ENABLED 0 [get_drc_checks {DSPS-5}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-21}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-25}]

    set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets]

    place_design -directive Quick
    route_design -directive Quick

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
    write_pip_txtdata design.txt
}

run
