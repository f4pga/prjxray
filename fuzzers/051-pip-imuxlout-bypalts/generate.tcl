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
read_verilog $::env(FUZDIR)/picorv32.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports din]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports dout]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports stb]

create_pblock roi
resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]
set_param tcl.collectionResultDisplayLimit 0

place_design
route_design

# write_checkpoint -force design.dcp

proc find_dst_pin {tile dst_wire} {
    # This function finds a CLB pin in a $tile which can be driven by the $dst_wire.
    # The pin may not be directly driven by the wire, so the function follows possible
    # routing path until it finds the desired pin.
    puts "Looking for dst pin for wire $tile/$dst_wire"
    set next_dst_wire $dst_wire
    set iterations 0
    while {$iterations < 10} {
        set iterations [expr $iterations + 1]
        set clb_dst_wire [get_wires -filter {TILE_NAME =~ CLB*} -of_objects [get_nodes -of_objects [get_wire $tile/$next_dst_wire]]]
        # the selected wire does not connect to any CLB wire let's go further and try to find a CLB pin
        if {$clb_dst_wire == ""} {
            # BOUNCE* pips may lead to a different CLB
            set pips [get_pips -regexp -downhill -of_objects [get_wire $tile/$next_dst_wire] (?!.*BOUNCE).*]
            # choose a random pip and check if it will lead us to a CLB
            set next_pip [lindex $pips [expr {int(rand()*[llength $pips])}]]
            set next_dst_wire [regsub {.*->>(.*)} $next_pip {\1}]
        } else {
            set clb_dst_pin [get_site_pins -of_objects [get_nodes -downhill -of_objects [get_pips -of_objects $clb_dst_wire]]]
            return $clb_dst_pin
        }
    }
    error "ERROR: Unable to find destination pin for wire $tile/$dst_wire (iterations: $iterations)"
}

proc find_src_pin {tile src_wire} {
    # This function finds a CLB pin in a $tile which can drive the $src_wire
    # The wire may not be directly driven by the pin, so the function follows
    # possible routing path until it finds the desired pin.
    puts "Looking for src pin for wire $tile/$src_wire"
    set next_src_wire $src_wire
    set iterations 0
    while {$iterations < 10} {
        set iterations [expr $iterations + 1]
        set clb_src_wire [get_wires -filter {TILE_NAME =~ CLB*} -of_objects [get_nodes -of_objects [get_wire $tile/$next_src_wire]]]
        # the selected wire does not connect to any CLB wire let's go further and try to find a CLB pin
        if {$clb_src_wire == ""} {
            set pips [get_pips -uphill -of_objects [get_wire $tile/$next_src_wire]]
            # choose a random pip and check if it will lead us to a CLB
            set next_pip [lindex $pips [expr {int(rand()*[llength $pips])}]]
            set next_src_wire [regsub {(.*)->>.*} $next_pip {\1}]
        } else {
            set clb_src_pin [get_site_pins -of_objects [get_nodes -uphill -of_objects [get_pips -of_objects $clb_src_wire]]]
            return $clb_src_pin
        }
    }
    error "ERROR: Unable to find source pin for $tile/$src_wire (iterations: $iterations)"
}

set fp [open "../../todo.txt" r]
set todo_lines {}
for {gets $fp line} {$line != ""} {gets $fp line} {
    lappend todo_lines [split $line .]
}
close $fp

set int_l_tiles [filter [pblock_tiles roi] {TYPE == INT_L}]]
set int_r_tiles [filter [pblock_tiles roi] {TYPE == INT_R}]]

for {set idx 0} {$idx < [llength $todo_lines]} {incr idx} {
    set line [lindex $todo_lines $idx]

    set tile_type [lindex $line 0]
    set dst_wire [lindex $line 1]
    set src_wire [lindex $line 2]

    if {$tile_type == "INT_L"} {set tile [lindex $int_l_tiles $idx]}
    if {$tile_type == "INT_R"} {set tile [lindex $int_r_tiles $idx]}

    set clb_dst_pin [find_dst_pin $tile $dst_wire]
    set clb_src_pin [find_src_pin $tile $src_wire]

    set src_prefix [regsub {(.*/.).*} ${clb_src_pin} {\1}]
    set dst_prefix [regsub {(.*/.).*} ${clb_dst_pin} {\1}]

    set slice [get_sites -of_objects $clb_dst_pin]
    set src_slice [get_sites -of_objects $clb_src_pin]
    set lut [regsub {.*/} $src_prefix {}]6LUT
    set dff [regsub {.*/} $src_prefix {}]FF

    set mynet [create_net mynet_$idx]
    set mylut [create_cell -reference LUT1 mylut_$idx]
    set dst_type [regsub {.*(.$)} $clb_dst_pin {\1}]
    set lutin [regsub {.*(.)} $clb_dst_pin {A\1}]

    # some dst pins are not LUT inputs so they do not have LOCK_PINS property
    if { $dst_type >= 0 && $dst_type <= 6 } {
        set_property -dict "LOC $slice BEL $lut LOCK_PINS I0:$lutin" $mylut
    } else {
        set_property -dict "LOC $slice BEL $lut" $mylut
    }

    # some source wires may be FF outputs, in such cases
    # we need to place and route an FF

    set src_type [regsub {.*/*(.$)} $clb_src_pin {\1}]
    if { $src_type == "Q" } {
        set mydff [create_cell -reference FDCE mydff_$idx]
        set_property -dict "LOC $src_slice BEL $dff" $mydff
        connect_net -net $mynet -objects "$mylut/I0 $mydff/Q"
    } else {
        connect_net -net $mynet -objects "$mylut/I0 $mylut/O"
    }

    set route_list "$tile/$src_wire $tile/$dst_wire"
    puts "route_via $mynet $route_list"
    set rc [route_via $mynet $route_list 0]
    if {$rc != 0} {
        puts "SUCCESS"
    } else {
        puts "Manual routing failed"
        # TODO: We should probably fail here
    }
}

route_design
write_checkpoint -force design.dcp
write_bitstream -force design.bit

# quick: only analyze manually routed tiles, skipping riscv and such
if {[info exists ::env(QUICK) ] && "$::env(QUICK)" == "Y"} {
    set lim [expr [llength $todo_lines] - 1]
    set tiles [concat [lrange $int_l_tiles 0 $lim] [lrange $int_r_tiles 0 $lim]]
} else {
    set tiles [get_tiles [regsub -all {CLBL[LM]} [get_tiles -of_objects [get_sites -of_objects [get_pblocks roi]]] INT]]
}

write_pip_txtdata design.txt
