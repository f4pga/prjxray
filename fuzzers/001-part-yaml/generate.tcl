# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
proc extract_iobanks {filename} {
    set fp [open $filename "w"]
    foreach iobank [get_iobanks] {
        set sample_site [lindex [get_sites -of $iobank] 0]
        if {[llength $sample_site] == 0} continue
        set clock_region [get_property CLOCK_REGION $sample_site]
        foreach tile [concat [get_tiles -filter {TYPE=~HCLK_IOI3}] [get_tiles -filter {TYPE=~HCLK_IOI}]] {
            set tile_sites [get_sites -of_object $tile]
            if {[llength $tile_sites] == 0} continue
            set hclk_tile_clock_region [get_property CLOCK_REGION [lindex [get_sites -of_object $tile] 0]]
            if {$clock_region == $hclk_tile_clock_region} {
                set coord [lindex [split $tile "_"] 2]
                puts $fp "$iobank,$coord"
            }
        }
    }
    close $fp
}

create_project -force -part $::env(XRAY_PART) design design

read_verilog ../../top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports di]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports do]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports stb]

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_param tcl.collectionResultDisplayLimit 0

set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]

place_design
route_design

extract_iobanks iobanks.txt
write_checkpoint -force design.dcp

# Write a normal bitstream that will do a singe FDRI write of all the frames.
write_bitstream -force design.bit

# Write a perframecrc bitstream which writes each frame individually followed by
# the frame address.  This shows where there are gaps in the frame address
# space.
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
write_bitstream -force design.perframecrc.bit
set_property BITSTREAM.GENERAL.PERFRAMECRC NO [current_design]
