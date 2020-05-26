# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
# Writes a JSON5 to filename containing timing for current design.
# This can be used with create_timing_worksheet_db.py to compare prjxray model
# with Vivado timing model outputs.
proc write_timing_info {filename} {
    set fp [open $filename w]
    puts $fp "\["

    set nets [get_nets]
    set idx 0
    foreach net $nets {
        puts "net: $net ($idx / [llength $nets])"
        incr idx
        if { $net == "<const0>" || $net == "<const1>" } {
            continue
        }

        if { [get_property TYPE [get_nets $net]] == "GROUND" } {
            continue
        }
        if { [get_property TYPE [get_nets $net]] == "POWER" } {
            continue
        }
        if { [get_property ROUTE_STATUS [get_nets $net]] == "INTRASITE" } {
            continue
        }
        if { [get_property ROUTE_STATUS [get_nets $net]] == "NOLOADS" } {
            continue
        }

        puts $fp "{"
            puts $fp "\"net\":\"$net\","

            set route [get_property ROUTE $net]
            puts $fp "\"route\":\"$route\","

            set pips [get_pips -of_objects $net]
            puts $fp "\"pips\":\["
            foreach pip $pips {
                puts $fp "{"
                    puts $fp "\"name\":\"$pip\","
                    puts $fp "\"src_wire\":\"[get_wires -uphill -of_objects $pip]\","
                    puts $fp "\"dst_wire\":\"[get_wires -downhill -of_objects $pip]\","
                    puts $fp "\"speed_index\":\"[get_property SPEED_INDEX $pip]\","
                    puts $fp "\"is_directional\":\"[get_property IS_DIRECTIONAL  $pip]\","
                puts $fp "},"
            }
            puts $fp "\],"
            puts $fp "\"nodes\":\["
            set nodes [get_nodes -of_objects $net]
            foreach node $nodes {
                puts $fp "{"
                    puts $fp "\"name\":\"$node\","
                    puts $fp "\"cost_code\":\"[get_property COST_CODE $node]\","
                    puts $fp "\"cost_code_name\":\"[get_property COST_CODE_NAME $node]\","
                    puts $fp "\"speed_class\":\"[get_property SPEED_CLASS $node]\","
                    puts $fp "\"wires\":\["
                    set wires [get_wires -of_objects $node]
                    foreach wire $wires {
                        puts $fp "{"
                            puts $fp "\"name\":\"$wire\","
                            puts $fp "\"cost_code\":\"[get_property COST_CODE $wire]\","
                            puts $fp "\"speed_index\":\"[get_property SPEED_INDEX $wire]\","
                        puts $fp "},"
                    }
                    puts $fp "\],"
                puts $fp "},"
            }
            puts $fp "\],"

            set opin [get_pins -leaf -of_objects [get_nets $net] -filter {DIRECTION == OUT}]
            puts $fp "\"opin\": {"
                puts $fp "\"name\":\"$opin\","
                set opin_site_pin [get_site_pins -of_objects $opin]
                puts $fp "\"site_pin\":\"$opin_site_pin\","
                puts $fp "\"site_pin_speed_index\":\"[get_property SPEED_INDEX $opin_site_pin]\","
                puts $fp "\"node\":\"[get_nodes -of_objects $opin_site_pin]\","
                puts $fp "\"wire\":\"[get_wires -of_objects [get_nodes -of_objects $opin_site_pin]]\","
            puts $fp "},"
            set ipins [get_pins -of_objects [get_nets $net] -filter {DIRECTION == IN} -leaf]
            puts $fp "\"ipins\":\["
            foreach ipin $ipins {
                set ipin_site_pin [get_site_pins -of_objects $ipin -quiet]
                if { $ipin_site_pin == "" } {
                    # This connection is internal!
                    continue
                }
                puts $fp "{"
                    set delay [get_net_delays -interconnect_only -of_objects $net -to $ipin]
                    puts $fp "\"name\":\"$ipin\","
                    puts $fp "\"ic_delays\":{"
                        foreach prop {"FAST_MAX" "FAST_MIN" "SLOW_MAX" "SLOW_MIN"} {
                            puts $fp "\"$prop\":\"[get_property $prop $delay]\","
                        }
                    puts $fp "},"
                    puts $fp "\"site_pin\":\"$ipin_site_pin\","
                    puts $fp "\"site_pin_speed_index\":\"[get_property SPEED_INDEX $ipin_site_pin]\","
                    puts $fp "\"node\":\"[get_nodes -of_objects $ipin_site_pin]\","
                    puts $fp "\"wire\":\"[get_wires -of_objects [get_nodes -of_objects $ipin_site_pin]]\","
                puts $fp "},"
            }
            puts $fp "\],"

        puts $fp "},"
    }

    puts $fp "\]"
    close $fp
}
