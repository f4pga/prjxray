# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
proc run {} {
    create_project -force -part $::env(XRAY_PART) design design
    read_verilog top.v
    synth_design -top top

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

    set_property IS_ENABLED 0 [get_drc_checks {NSTD-1}]
    set_property IS_ENABLED 0 [get_drc_checks {UCIO-1}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-48}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-47}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-1619}]
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-17}]
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-18}]
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-19}]
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-19}]
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-20}]
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-20}]
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-21}]
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-22}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-51}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-51}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-51}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-51}]
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-23}]

    place_design
    route_design

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
}

run
