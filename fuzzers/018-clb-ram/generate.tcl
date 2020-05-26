# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
proc build {} {
    create_project -force -part $::env(XRAY_PART) design design
    read_verilog top.v
    synth_design -top top

    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports stb]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports di]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports do]

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
    write_bitstream -force design.bit
}

proc dump {} {
    set roi [get_pblocks roi]

    set fp [open "design.csv" w]
    puts $fp "tile,site,bel,cell,ref_name,prim_type"

    set sites [get_sites -of_objects $roi]
    for {set sitei 0} {$sitei < [llength $sites]} {incr sitei} {
        # set site [get_sites SLICE_X6Y105]
        set site [lindex $sites $sitei]
        set tile [get_tiles -of_objects $site]

        set bels [get_bels -of_objects $site -filter {TYPE == LUT_OR_MEM6}]
        for {set beli 0} {$beli < [llength $bels]} {incr beli} {
            # set bel [get_bels SLICE_X6Y105/D6LUT]
            set bel [lindex $bels $beli]
            set cell [get_cells -of_objects $bel]
            if { "$cell" == "" } {
                continue
            }
            # Ex SRL16E
            set ref_name [get_property REF_NAME $cell]
            # Ex: DMEM.srl.SRL16E
            set prim_type [get_property PRIMITIVE_TYPE $cell]
            puts $fp "$tile,$site,$bel,$cell,$ref_name,$prim_type"
        }
    }
    close $fp
}

proc run {} {
    build
    dump
}

run
