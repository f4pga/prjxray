# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
source "$::env(XRAY_DIR)/utils/utils.tcl"

proc build_basic {} {
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
}

proc load_todo {} {
    set fp [open "../../todo.txt" r]
    set todo_lines {}
    for {gets $fp line} {$line != ""} {gets $fp line} {
        lappend todo_lines [split $line .]
    }
    close $fp
    return $todo_lines
}

proc lremove { l val } {
    set idx [lsearch $l $val]
    return [lreplace $l $idx $idx]
}

proc route_todo {} {
    set todo_lines [load_todo]
    set int_l_tiles [filter [pblock_tiles roi] {TYPE == INT_L}]
    set int_r_tiles [filter [pblock_tiles roi] {TYPE == INT_R}]

    for {set idx 0} {$idx < [llength $todo_lines]} {incr idx} {
        set line [lindex $todo_lines $idx]
        puts ""
        puts ""
        puts "== $idx: $line"
        set tile_type [lindex $line 0]
        set dst_wire [lindex $line 1]
        set src_wire [lindex $line 2]

        set mylut [create_cell -reference LUT1 mylut_$idx]
        set mynet [create_net mynet_$idx]
        connect_net -net $mynet -objects "$mylut/I0 $mylut/O"

        set tries 0
        while {1} {
            incr tries

            puts ""
            puts "$mynet: try $tries"
            if {$tile_type == "INT_L"} {
                set tile [randsample_list 1 $int_l_tiles]
                set int_l_tiles [lremove $int_l_tiles $tile]
                set other_tile [randsample_list 1 $int_r_tiles]
                set int_r_tiles [lremove $int_r_tiles $other_tile]
            } elseif {$tile_type == "INT_R"} {
                set tile [randsample_list 1 $int_r_tiles]
                set int_r_tiles [lremove $int_r_tiles $tile]
                set other_tile [randsample_list 1 $int_l_tiles]
                set int_l_tiles [lremove $int_l_tiles $other_tile]
            } else {
                error "Bad tile type $tile_type"
            }
            puts "PIP Tile: $tile, LUT tile: $other_tile"

            set driver_site [get_sites -of_objects [get_site_pins -of_objects [get_nodes -downhill \
                    -of_objects [get_nodes -of_objects [get_wires $other_tile/CLK*0]]]]]
            puts "LUT site: $driver_site"
            set_property -dict "LOC $driver_site BEL A6LUT" $mylut

            set route_list "$tile/$src_wire $tile/$dst_wire"
            puts "route_via $mynet $route_list"
            set rc [route_via $mynet $route_list 0]
            if {$rc != 0} {
                break
            }

            puts "WARNING: failed to route net"
            write_checkpoint -force route_todo_$idx.$tries.fail.dcp

            puts "Rolling back route"
            set_property is_route_fixed 0 $mynet
            set_property is_bel_fixed 0 $mylut
            set_property is_loc_fixed 1 $mylut
            route_design -unroute -nets $mynet

            # sometimes it gets stuck in specific orientations
            if {$tries >= 3} {
                puts "WARNING: failed to route net after $tries tries"
                break
            }
        }
    }
}

proc run {} {
    build_basic
    route_todo
    route_design

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
    write_pip_txtdata design.txt
}

run
