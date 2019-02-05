puts "FUZ([pwd]): Creating project"
create_project -force -part $::env(XRAY_PART) design design

puts "FUZ([pwd]): Reading verilog"
read_verilog top.v

puts "FUZ([pwd]): Synth design"
synth_design -top top

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

set_param tcl.collectionResultDisplayLimit 0

source "$::env(XRAY_DIR)/utils/utils.tcl"

puts "FUZ([pwd]): Placing design"
place_design
puts "FUZ([pwd]): Routing design"
route_design

write_checkpoint -force design.dcp

write_bitstream -force design.bit
write_pip_txtdata design.txt
