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
        if [string match IOB33* [get_property SITE_TYPE $site]] {
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

    puts "Looping"
    for {set idx 0} {$idx < [llength $pin_lines]} {incr idx} {
        set line [lindex $pin_lines $idx]
        puts "$line"

        set site_str [lindex $line 1]
        set pin_str [lindex $line 2]
        set iostandard [lindex $line 3]
        set drive [lindex $line 4]
        set slew [lindex $line 5]
        set pulltype [lindex $line 6]

        # Have: site
        # Want: pin for site

        set site [get_sites $site_str]
        set pad_bel [get_bels -of_objects $site -filter {TYPE =~ PAD && NAME =~ IOB_*}]
        # set port [get_ports -of_objects $site]
        set port [get_ports $pin_str]
        set tile [get_tiles -of_objects $site]

        set pin [dict get $io_pin_sites $site]

        set props {}
        #lappend props PACKAGE_PIN $pin
        lappend props IOSTANDARD $iostandard
        lappend props PULLTYPE $pulltype

        if {$drive != "None"} {
            lappend props DRIVE $drive
        }

        if {$slew != "None"} {
            lappend props SLEW $slew
        }

        puts $props

        set_property -dict "$props" $port
    }
}

proc run {} {
    create_project -force -part $::env(XRAY_PART) design design
    read_verilog top.v
    synth_design -top top

    loc_pins

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-79}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-144}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-150}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-152}]

    write_checkpoint -force design_pre_place.dcp

    place_design
    route_design

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
}

run
