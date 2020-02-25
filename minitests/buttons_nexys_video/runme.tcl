create_project -force -part $::env(XRAY_PART) design design
read_verilog ../buttons_nexys_video.v
read_xdc ../buttons_nexys_video.xdc

synth_design -top top -flatten_hierarchy none
place_design
route_design

write_checkpoint -force design.dcp
write_bitstream -force design.bit
