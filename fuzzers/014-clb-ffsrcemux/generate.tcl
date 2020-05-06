# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
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



# Get all FF's in pblock
set ffs [get_bels -of_objects [get_sites -of_objects [get_pblocks roi]] -filter {TYPE =~ *} */*FF]

set fp [open "design.txt" w]
# set ff [lindex $ffs 0]
# set ff [get_bels SLICE_X23Y100/AFF]
# proc putl {lst} { foreach line $lst {puts $line} }
foreach ff $ffs {
    set tile [get_tile -of_objects $ff]
    set grid_x [get_property GRID_POINT_X $tile]
    set grid_y [get_property GRID_POINT_Y $tile]
    set type [get_property TYPE $tile]
    set bel_type [get_property TYPE $ff]
    set used [get_property IS_USED $ff]
    set usedstr ""
    if $used {
        set ffc [get_cells -of_objects $ff]
        set cell_bel [get_property BEL $ffc]
        # ex: FDRE
        set ref_name [get_property REF_NAME $ffc]
        #set cinv [get_property IS_C_INVERTED $ffc]

        set cpin [get_pins -of_objects $ffc -filter {REF_PIN_NAME == C}]
        set cinv [get_property IS_INVERTED $cpin]
        set usedstr "$cell_bel $ref_name $cinv"
    }
    puts $fp "$type $tile $grid_x $grid_y $ff $bel_type $used $usedstr"
}
close $fp
