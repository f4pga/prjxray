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

proc dump_tile_timings {tile timing_fp config_fp pins_fp tile_pins_fp} {

    set properties [list "DELAY" "FAST_MAX" "FAST_MIN" "SLOW_MAX" "SLOW_MIN"]
    set timing_line {}
    set config_line {}
    set pins_line {}
    set tile_pins_line {}

    lappend timing_line [get_property TYPE $tile]
    lappend config_line [get_property TYPE $tile]
    lappend pins_line [get_property TYPE $tile]
    lappend tile_pins_line [get_property TYPE $tile]

    set sites [get_sites -of_objects [get_tiles $tile]]

    lappend tile_pins_line [llength $sites]
    lappend timing_line [llength $sites]
    lappend config_line [llength $sites]
    lappend pins_line [llength $sites]

    foreach site $sites {
        set site_type [get_property SITE_TYPE $site]

        lappend tile_pins_line $site_type
        lappend pins_line $site_type
        lappend timing_line $site_type
        lappend config_line $site_type

        # dump site pins
        set site_pins [get_site_pins -of_objects [get_sites $site]]
        lappend tile_pins_line [llength $site_pins]

        foreach pin $site_pins {
            set direction [get_property DIRECTION $pin]
            set is_part_of_bus [get_property IS_PART_OF_BUS $pin]
            regexp {\/(.*)$} $pin -> pin
            lappend tile_pins_line $pin $direction $is_part_of_bus
        }

        # dump bel pins, speed_models and configs
        set bels [get_bels -of_objects $site]

        lappend pins_line [llength $bels]
        lappend timing_line [llength $bels]
        lappend config_line [llength $bels]

        foreach bel $bels {
            set speed_models [get_speed_models -of_objects $bel]
            set bel_type [get_property TYPE $bel]
            set bel_configs [list_property $bel CONFIG*]
            set bel_pins [get_bel_pins -of_objects [get_bels $bel]]

            lappend pins_line $bel_type
            lappend pins_line [llength $bel_pins]
            foreach pin $bel_pins {
                set direction [get_property DIRECTION $pin]
                set is_clock [get_property IS_CLOCK $pin]
                set is_part_of_bus [get_property IS_PART_OF_BUS $pin]
                regexp {\/.*\/(.*)$} $pin -> pin
                lappend pins_line $pin $direction $is_clock $is_part_of_bus
            }

            lappend config_line $bel_type
            lappend config_line [llength $bel_configs]
            foreach config $bel_configs {
                set config_vals [get_property $config $bel]
                lappend config_line $config
                lappend config_line [llength $config_vals]
                foreach val $config_vals {
                    lappend config_line $val
                }
            }

            lappend timing_line "$bel_type"
            lappend timing_line [llength $speed_models]
            foreach speed_model $speed_models {
                lappend timing_line $speed_model
                foreach property $properties {
                    set value [get_property $property $speed_model]
                    lappend timing_line "$property:$value"
                }
            }
        }
    }


    puts $tile_pins_fp $tile_pins_line
    puts $pins_fp $pins_line
    puts $timing_fp $timing_line
    puts $config_fp $config_line
}

proc dump {} {

    set types [get_tile_types]
    set timing_fp [open "bel_timings.txt" w]
    set property_fp [open "bel_properties.txt" w]
    set pins_fp [open "bel_pins.txt" w]
    set tile_pins_fp [open "tile_pins.txt" w]
    foreach type $types {
        set tile [randsample_list 1 [get_tiles -filter "TYPE == $type"]]
        dump_tile_timings $tile $timing_fp $property_fp $pins_fp $tile_pins_fp
    }

    set other_site_types [list ISERDESE2 OSERDESE2]
    foreach site_type $other_site_types {
        set cell [create_cell -reference $site_type test]
        place_design
        set tile [get_tiles -of [get_sites -of $cell]]
        dump_tile_timings $tile $timing_fp $property_fp $pins_fp $tile_pins_fp
        unplace_cell $cell
        remove_cell $cell
    }

    close $pins_fp
    close $timing_fp
    close $property_fp
}

proc run {} {
    create_design
    place_and_route_design
    dump
    write_bitstream -force design.bit
}

run
