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

write_checkpoint -force design.dcp

set net [get_nets o_OBUF]

if [regexp "_001$" [pwd]] {
    set hclk_tiles [filter [roi_tiles] {TYPE == HCLK_L}]
} elseif [regexp "_002$" [pwd]] {
    set hclk_tiles [filter [roi_tiles] {TYPE == HCLK_R}]
} else {
    error "unknown specimen"
}

# set tile [randsample_list 1 $hclk_tiles]
set tile [lindex $hclk_tiles end]
puts "Selected tile $tile"
set pips [get_pips -of_objects $tile]

for {set i 0} {$i < [llength $pips]} {incr i} {
    set pip [lindex $pips $i]
    set_property IS_ROUTE_FIXED 0 $net
    route_design -unroute -net $net
    set n1 [get_nodes -uphill -of_objects $pip]
    set n2 [get_nodes -downhill -of_objects $pip]
    route_via $net "$n1 $n2"
    write_checkpoint -force design_$i.dcp
    write_bitstream -force design_$i.bit
    set fp [open "design_$i.txt" w]
    puts $fp "$tile $pip"
    close $fp
}
