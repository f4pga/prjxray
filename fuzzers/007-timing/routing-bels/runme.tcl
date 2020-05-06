# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
source "$::env(XRAY_DIR)/utils/utils.tcl"

proc create_design {} {

    create_project -force -part $::env(XRAY_PART) design design
    read_verilog $::env(SRC_DIR)/top.v
    synth_design -top top -flatten_hierarchy none

    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports di]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports do]

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
}

proc place_and_route_design {} {

    place_design
    route_design

    write_checkpoint -force design.dcp
}

proc dump_model_timings {timing_fp models} {

    set properties [list "DELAY" "FAST_MAX" "FAST_MIN" "SLOW_MAX" "SLOW_MIN"]

    foreach model $models {
        set timing_line {}
        lappend timing_line "$model"
        foreach property $properties {
            set value [get_property $property [get_speed_models -patterns $model]]
            lappend timing_line "$property:$value"
        }

        puts $timing_fp $timing_line
    }
}

proc dump {} {

    set slicel_fp [open "slicel.txt" w]
    set slicem_fp [open "slicem.txt" w]
    set slicel_speed_models [get_speed_models -patterns *_sl_*]
    set slicem_speed_models [get_speed_models -patterns *_sm_*]

    dump_model_timings $slicel_fp $slicel_speed_models
    dump_model_timings $slicem_fp $slicem_speed_models

    close $slicel_fp
    close $slicem_fp
}

proc run {} {
    create_design
    place_and_route_design
    dump
    write_bitstream -force design.bit
}

run
