# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
source "$::env(XRAY_DIR)/utils/utils.tcl"
proc randsample_list_unique {num lst {axis ""}} {
    set rlst {}
    set coords {}
    set regexp_string {[A-Z_]+(X[0-9]+)(Y[0-9]+)}
    for {set i 0} {$i<$num} {incr i} {
        set j [expr {int(rand()*[llength $lst])}]
        set element [lindex $lst $j]
        if {$axis != ""} {
            regexp $regexp_string $element dummy x_coord y_coord
            set attempts 0
            if {$axis == "X"} {
                while {[lsearch -regexp $rlst "\[A-Z_\]+${x_coord}Y\[0-9\]+"] >= 0 && $attempts < 10} {
                    incr attempts
                    set j [expr {int(rand()*[llength $lst])}]
                    set element [lindex $lst $j]
                    regexp $regexp_string $element dummy x_coord y_coord
                }
            } elseif {$axis == "Y"} {
                while {[lsearch -regexp $rlst "\[A-Z_\]+X\[0-9\]+${y_coord}"] >= 0 && $attempts < 10} {
                    incr attempts
                    set j [expr {int(rand()*[llength $lst])}]
                    set element [lindex $lst $j]
                    regexp $regexp_string $element dummy x_coord y_coord
                }
            }
        }
        lappend rlst $element
        set lst [lreplace $lst $j $j]
    }
    return $rlst
}

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


set fp [open "../../todo.txt" r]
set todo_lines {}
for {gets $fp line} {$line != ""} {gets $fp line} {
    lappend todo_lines [split $line .]
}
close $fp

set tiles [llength $todo_lines]

set int_l_tiles [randsample_list_unique $tiles [filter [pblock_tiles roi] {TYPE == INT_L}] "X"]
set int_r_tiles [randsample_list_unique $tiles [filter [pblock_tiles roi] {TYPE == INT_R}] "X"]
set to_nodes {}
set src_wires {}
set dst_wires {}

for {set idx 0} {$idx < [llength $todo_lines]} {incr idx} {
    set line [lindex $todo_lines $idx]
    puts "== $idx: $line"

    set tile_type [lindex $line 0]
    set dst_wire [lindex $line 1]
    if {[lsearch $dst_wires $dst_wire] >= 0} {
        puts "DESTINATION WIRE ALREADY USED - SKIPPING"
        continue
    }
    lappend dst_wires $dst_wire

    set src_wire [lindex $line 2]
    if {[lsearch $src_wires $src_wire] >= 0} {
        puts "SOURCE WIRE ALREADY USED - SKIPPING"
        continue
    }
    lappend src_wires $src_wire

    set mylut [create_cell -reference LUT1 mylut_$idx]
    set myff [create_cell -reference FDRE myff_$idx]

    set mynet [create_net mynet_$idx]
    connect_net -net $mynet -objects "$mylut/O $myff/C"

    set tile_idx $idx
    if {$tile_type == "INT_L"} {set tile [lindex $int_l_tiles $tile_idx]; set other_tile [lindex $int_r_tiles $tile_idx]}
    if {$tile_type == "INT_R"} {set tile [lindex $int_r_tiles $tile_idx]; set other_tile [lindex $int_l_tiles $tile_idx]}

    set driver_site [get_sites -of_objects [get_site_pins -of_objects [get_nodes -downhill \
            -of_objects [get_nodes -of_objects [get_wires $other_tile/CLK*0]]]]]

    set recv_site [get_sites -of_objects [get_site_pins -of_objects [get_nodes -downhill \
            -of_objects [get_nodes -of_objects [get_wires $tile/$dst_wire]]]]]

    set_property -dict "LOC $driver_site BEL A6LUT" $mylut
    set ffbel [lindex "AFF A5FF BFF B5FF CFF C5FF DFF D5FF" [expr {int(rand()*8)}]]
    set_property -dict "LOC $recv_site BEL $ffbel" $myff

    puts "ffbel $ffbel"
    puts "tile $tile"
    puts "other tile: $other_tile"
    set to_node_name_dst [get_nodes -of_objects [get_wires $tile/$dst_wire]]
    puts "to_node_name_dst: $to_node_name_dst"
    if {[regexp {[A-Z_]+(X[0-9]+)(Y[0-9]+)} $to_node_name_dst dummy x_coord_dst y_coord_dst]} {
        if {[lsearch $to_nodes $x_coord_dst] == -1} {
            lappend to_nodes $x_coord_dst
        } else {
            puts "TO_NODE ALREADY USED - SKIPPING"
            continue
        }
    }
    set to_node_name_src [get_nodes -of_objects [get_wires $tile/$src_wire]]
    puts "to_node_name_src: $to_node_name_src"
    if {[regexp {[A-Z_]+(X[0-9]+)(Y[0-9]+)} $to_node_name_src dummy x_coord_src y_coord_src]} {
        if {[lsearch $to_nodes $x_coord_src] == -1} {
            lappend to_nodes $x_coord_src
        } elseif {$x_coord_src != $x_coord_dst} {
            puts "TO_NODE ALREADY USED - SKIPPING"
            continue
        }
    }

    set rc [route_via $mynet "$tile/$src_wire $tile/$dst_wire" 0]
    if {$rc != 0} {
        puts "ROUTING DONE!"
        continue
    }

    write_checkpoint -force route_todo_$idx.fail.dcp
    error "ERROR: failed to route net"
}

route_design
write_checkpoint -force design.dcp
write_bitstream -force design.bit
write_pip_txtdata design.txt
