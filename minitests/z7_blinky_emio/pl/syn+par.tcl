create_project -force -name $env(PROJECT_NAME) -part $env(VIVADO_PART)

read_verilog ../$env(PROJECT_NAME).v
synth_design -top top

source ../zybo.xdc

place_design
route_design

write_checkpoint -force ../$env(PROJECT_NAME).dcp
write_bitstream  -force ../$env(PROJECT_NAME).bit
