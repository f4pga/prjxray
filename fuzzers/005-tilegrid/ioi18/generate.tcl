# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
source "$::env(XRAY_DIR)/utils/utils.tcl"

proc make_io_pin_sites {} {
    # get all possible IOB pins
    foreach pad [get_package_pins -filter "IS_GENERAL_PURPOSE == 1"] {
        set site [get_sites -of_objects $pad]
        if {[llength $site] == 0} {
            continue
        }
        if [string match IOB18* [get_property SITE_TYPE $site]] {
            dict append io_pin_sites $site $pad
        }
    }
    return $io_pin_sites
}

proc load_pin_lines {} {
    # IOB_X0Y103 clk input
    # IOB_X0Y129 do[0] output

    set fp [open "params.csv" r]
    gets $fp line

    set pin_lines {}
    for {gets $fp line} {$line != ""} {gets $fp line} {
        lappend pin_lines [split $line ","]
    }
    close $fp
    return $pin_lines
}

proc loc_pins {} {
    set pin_lines [load_pin_lines]
    set io_pin_sites [make_io_pin_sites]
    set package_pin_keys [dict keys $io_pin_sites]

    puts "Looping"
    for {set idx 0} {$idx < [llength $pin_lines]} {incr idx} {
        set line [lindex $pin_lines $idx]
        puts "$line"

        set site_str [lindex $line 2]
        set pin_str [lindex $line 3]
        set pad_str [lindex $line 4]

        # Have: site
        # Want: pin for site

        set site [get_sites $site_str]
        set port [get_ports $pin_str]
        set tile [get_tiles -of_objects $site]


        set pin [dict get $io_pin_sites $pad_str]
        set_property -dict "PACKAGE_PIN $pin IOSTANDARD LVCMOS18" $port
    }
}

proc run {} {
    create_project -force -part $::env(XRAY_PART) design design
    read_verilog top.v
    synth_design -top top

    #loc_pins

    set_property CFGBVS GND [current_design]
    set_property CONFIG_VOLTAGE 1.8 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-79}]
    set_property SEVERITY {Warning} [get_drc_checks NSTD-1]
    set_property SEVERITY {Warning} [get_drc_checks UCIO-1]
    #set_property IS_ENABLED 0 [get_drc_checks {REQP-83}]

    place_design
    route_design

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
}

run
