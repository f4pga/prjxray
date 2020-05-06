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

    set fp [open "$::env(SRC_DIR)/params.csv" r]
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
    foreach line $pin_lines {
        puts "$line"
        lassign $line site_str pin_str io cell_str

        # Have: site
        # Want: pin for site
        set site [get_sites $site_str]
        #set pad_bel [get_bels -of_objects $site -filter {TYPE =~ PAD && NAME =~ IOB_*}]
        # set port [get_ports -of_objects $site]
        set port [get_ports $pin_str]
        set tile [get_tiles -of_objects $site]
        set pin [dict get $io_pin_sites $site]
        set iostandard [get_property IOSTANDARD $port]

        set_property -dict "PACKAGE_PIN $pin IOSTANDARD $iostandard" $port
    }
}

proc set_property_value_on_port {property value port} {
    set_property $property $value $port
    set got [get_property $property $port]
    if {"$got" != "$value"} {
        puts "Skipping: wanted $value, got $got"
        return 1
    }
    return 0
}

proc run {} {
    create_project -force -part $::env(XRAY_PART) design design
    read_verilog top.v
    synth_design -top top

    # Mostly doesn't matter since IOB are special, but add anyway
    create_pblock roi
    add_cells_to_pblock [get_pblocks roi] [get_cells roi]
    resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
    set_param tcl.collectionResultDisplayLimit 0

    loc_pins
    place_design
    route_design
    set pin_lines [load_pin_lines]
    # For HR Current Drive
    set property_dictionary [dict create \
            LVCMOS12 \
            [dict create DRIVE [list 4 8 12] SLEW [list SLOW FAST]] \
            LVCMOS15 \
            [dict create DRIVE [list 4 8 12 16] SLEW [list SLOW FAST]] \
            LVCMOS18 \
            [dict create DRIVE [list 4 8 12 16 24] SLEW [list SLOW FAST]] \
            LVCMOS25 \
            [dict create DRIVE [list 4 8 12 16] SLEW [list SLOW FAST]] \
            LVCMOS33 \
            [dict create DRIVE [list 4 8 12 16] SLEW [list SLOW FAST]] \
            LVTTL \
            [dict create DRIVE [list 4 8 12 16 24] SLEW [list SLOW FAST]] \
            ]
    #HSUL_12 no DRIVE support, only SLEW
    #HSTL_I, HSTL_II, HSTL_I_18, HSTL_II_18 no drive support, only SLEW
    #SSTL/18/135/ no drive support, only SLEW

    foreach iostandard [dict keys $property_dictionary] {
        foreach slew [dict get $property_dictionary $iostandard SLEW] {
            foreach drive [dict get $property_dictionary $iostandard DRIVE] {
                foreach line $pin_lines {
                    lassign $line site_str pin_str io cell_str
                    set port [get_ports $pin_str]

                    set_property IOSTANDARD $iostandard $port

                    if {$io == "input"} continue

                    if {[set_property_value_on_port SLEW $slew $port]} {
                        continue
                    }

                    if {[set_property_value_on_port DRIVE $drive $port]} {
                        continue
                    }
                }
                if {[catch {write_bitstream -force design_${iostandard}_${slew}_${drive}.bit} issue]} {
                    puts "WARNING failed to write: $issue"
                    continue
                }
                # Only write checkpoints for acceptable bitstreams
                write_checkpoint -force design_${iostandard}_${slew}_${drive}.dcp
            }
        }
    }
}
run
