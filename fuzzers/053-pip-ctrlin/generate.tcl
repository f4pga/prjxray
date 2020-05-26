# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
source "$::env(XRAY_DIR)/utils/utils.tcl"

create_project -force -part $::env(XRAY_PART) design design

read_verilog $::env(FUZDIR)/top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports i]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports o]

create_pblock roi
resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
set_param tcl.collectionResultDisplayLimit 0

place_design
route_design

# write_checkpoint -force design.dcp

# This function checks the input todo file to ensure there is enough stimulus.
# By default if the input todo file is bigger than the specified number of lines then
# it is used in the subsequent stages of the script.
# However, when the input todo is smaller then a todo file from a previous iteration,
# which meets the minimum lines requirement, gets chosen.
# This helps with increasing the stimuli without increasing the
# global number of specimen used in every iteration.
proc get_todo {{min_lines 0}} {
    if {[info exists ::env(ITER)]} {
        set current_iter $::env(ITER)
    } else {
        set current_iter 1
    }
    set todo_file "../../todo/${current_iter}_all.txt"
    lassign [exec wc -l $todo_file] line_count file_name
    if {$min_lines == 0} {
        return $file_name
    }
    if {$current_iter == 1 && $line_count < $min_lines} {
        error "ERROR: Initial TODO is too small"
    }
    while {$line_count < $min_lines} {
        incr current_iter -1
        set todo_file "../../todo/${current_iter}_all.txt"
        lassign [exec wc -l $todo_file] line_count file_name
    }
    return $file_name
}


set fp [open [get_todo 10] r]
set todo_lines {}
for {gets $fp line} {$line != ""} {gets $fp line} {
    lappend todo_lines [split $line .]
}
close $fp

# each run can fail up to three times so we need to prepare 3*todo_lines tiles to work on
set tiles [expr 3 * [llength $todo_lines]]

set int_l_tiles [randsample_list $tiles [filter [pblock_tiles roi] {TYPE == INT_L}]]
set int_r_tiles [randsample_list $tiles [filter [pblock_tiles roi] {TYPE == INT_R}]]

for {set idx 0} {$idx < [llength $todo_lines]} {incr idx} {
    set line [lindex $todo_lines $idx]
    puts "== $idx: $line"

    set tile_type [lindex $line 0]
    set dst_wire [lindex $line 1]
    set src_wire [lindex $line 2]
    set mylut [create_cell -reference LUT1 mylut_$idx]
    set myff [create_cell -reference FDRE myff_$idx]
    set mynet [create_net mynet_$idx]

    set tries 0
    while {1} {
        set tile_idx [expr $tries + [expr $idx * 3]]
        incr tries

        if {$tile_type == "INT_L"} {set tile [lindex $int_l_tiles $tile_idx]; set other_tile [lindex $int_r_tiles $tile_idx]}
        if {$tile_type == "INT_R"} {set tile [lindex $int_r_tiles $tile_idx]; set other_tile [lindex $int_l_tiles $tile_idx]}

        set driver_site [get_sites -of_objects [get_site_pins -of_objects [get_nodes -downhill \
                -of_objects [get_nodes -of_objects [get_wires $other_tile/CLK*0]]]]]

        set recv_site [get_sites -of_objects [get_site_pins -of_objects [get_nodes -downhill \
                -of_objects [get_nodes -of_objects [get_wires $tile/$dst_wire]]]]]

        set_property -dict "LOC $driver_site BEL A6LUT" $mylut

        set ffbel [lindex "AFF A5FF BFF B5FF CFF C5FF DFF D5FF" [expr {int(rand()*8)}]]
        set_property -dict "LOC $recv_site BEL $ffbel" $myff

        connect_net -net $mynet -objects "$mylut/O $myff/R"
        set rc [route_via $mynet "$tile/$src_wire $tile/$dst_wire" 0]
        if {$rc != 0} {
            puts "ROUTING DONE!"
            break
        }

        # fallback
        puts "WARNING: failed to route net"
        write_checkpoint -force route_todo_$idx.$tries.fail.dcp

        puts "Rolling back route"
        set_property is_route_fixed 0 $mynet
        set_property is_bel_fixed 0 $mylut
        set_property is_loc_fixed 1 $mylut
        set_property is_bel_fixed 0 $myff
        set_property is_loc_fixed 1 $myff
        route_design -unroute -nets $mynet

        # sometimes it gets stuck in specific src -> dst locations
        if {$tries >= 3} {
            error "ERROR: failed to route net after $tries tries"
        }
    }
}

route_design
write_checkpoint -force design.dcp
write_bitstream -force design.bit
write_pip_txtdata design.txt
