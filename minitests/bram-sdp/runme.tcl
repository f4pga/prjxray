create_project -force -part $::env(XRAY_PART) design design
read_verilog ../top.v
synth_design -top top -flatten_hierarchy none

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

place_design
route_design

set_property IS_ENABLED 0 [get_drc_checks {NSTD-1}]
set_property IS_ENABLED 0 [get_drc_checks {UCIO-1}]

write_checkpoint -force design.dcp
write_bitstream -force design.bit
