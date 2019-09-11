create_project -force -name $env(PROJECT_NAME) -part xc7a35tcpg236-1

read_edif ../$env(PROJECT_NAME).edif

link_design -part xc7a35tcpg236-1
source ../basys3.xdc

set_property SEVERITY {Warning} [get_drc_checks UCIO-1]
set_property SEVERITY {Warning} [get_drc_checks NSTD-1]
set_property SEVERITY {Warning} [get_drc_checks REQP-1936]

place_design
route_design

write_checkpoint -force ../$env(PROJECT_NAME).dcp

write_bitstream -force ../$env(PROJECT_NAME).bit
