# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
puts "FUZ([pwd]): Creating project"
create_project -force -part $::env(XRAY_PART) design design

puts "FUZ([pwd]): Reading verilog"
read_verilog top.v

puts "FUZ([pwd]): Synth design"
synth_design -top top

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

set_param tcl.collectionResultDisplayLimit 0

source "$::env(XRAY_DIR)/utils/utils.tcl"

puts "FUZ([pwd]): Placing design"
place_design
puts "FUZ([pwd]): Routing design"
route_design

write_checkpoint -force design.dcp

proc write_txtdata {filename} {
    puts "FUZ([pwd]): Writing $filename."
    set fp [open $filename w]
    foreach net [get_nets -hierarchical] {
        if [string match "*addr*" $net] {
            puts "Tick $net."
            foreach pip [get_pips -of_objects $net] {
                set tile [get_tiles -of_objects $pip]
                set src_wire [get_wires -uphill -of_objects $pip]
                set dst_wire [get_wires -downhill -of_objects $pip]
                set num_pips [llength [get_nodes -uphill -of_objects [get_nodes -of_objects $dst_wire]]]
                set dir_prop [get_property IS_DIRECTIONAL $pip]
                puts $fp "$tile $pip $src_wire $dst_wire $num_pips $dir_prop"
            }
        }
    }
    close $fp
}

write_bitstream -force design.bit
write_txtdata design.txt
