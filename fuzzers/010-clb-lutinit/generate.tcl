# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
create_project -force -part $::env(XRAY_PART) design design

read_verilog ../../top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports di]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports do]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports stb]

set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A5 I5:A6} \
        [get_cells -quiet -filter {REF_NAME == LUT6} -hierarchical]

create_pblock roi
add_cells_to_pblock [get_pblocks roi] [get_cells roi]
resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
set_param tcl.collectionResultDisplayLimit 0

set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]

place_design
route_design

write_checkpoint -force design.dcp


########################################
# Unmodified design with random LUTs

proc write_txtdata {filename} {
    puts "Writing $filename."
    set fp [open $filename w]
    foreach cell [get_cells -hierarchical -filter {REF_NAME == LUT6}] {
        set bel [get_property BEL $cell]
        set loc [get_property LOC $cell]
        set init [get_property INIT $cell]
        puts $fp "$loc $bel $init"
    }
    close $fp
}

write_bitstream -force design_0.bit
write_txtdata design_0.txt


########################################
# XOR LUT INITs

set pattern_list {
    0x1234567812345678
    0xFFFFFFFF00000000
    0xFFFF0000FFFF0000
    0xFF00FF00FF00FF00
    0xF0F0F0F0F0F0F0F0
    0xCCCCCCCCCCCCCCCC
    0xAAAAAAAAAAAAAAAA
}

set pattern_index 0

foreach cell [get_cells -hierarchical -filter {REF_NAME == LUT6}] {
    set v [get_property init $cell]
    set v [scan [string range $v 4 100] %x]
    set v [expr $v ^ [lindex $pattern_list $pattern_index]]
    set v [format %x $v]
    set_property init 64'h$v $cell
    set pattern_index [expr ($pattern_index + 1) % 7]
}

write_bitstream -force design_1.bit
write_txtdata design_1.txt


########################################
# Set LUT INITs

set pattern_index 1

foreach cell [get_cells -hierarchical -filter {REF_NAME == LUT6}] {
    set_property init 64'h[lindex $pattern_list $pattern_index] $cell
    set pattern_index [expr ($pattern_index + 1) % 7]
}

write_bitstream -force design_2.bit
write_txtdata design_2.txt
