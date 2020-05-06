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
read_verilog $::env(FUZDIR)/top.v
read_verilog $::env(FUZDIR)/picorv32.v

puts "FUZ([pwd]): Synth design"
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports din]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports dout]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports stb]

create_pblock roi
add_cells_to_pblock [get_pblocks roi] [get_cells roi]
resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]
set_param tcl.collectionResultDisplayLimit 0

source "$::env(XRAY_DIR)/utils/utils.tcl"
randplace_pblock 100 roi

puts "FUZ([pwd]): Placing design"
place_design
puts "FUZ([pwd]): Routing design"
route_design

write_checkpoint -force design.dcp

write_bitstream -force design.bit
write_pip_txtdata design.txt
