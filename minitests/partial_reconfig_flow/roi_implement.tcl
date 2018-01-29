open_checkpoint harness_impl.dcp
read_checkpoint -cell roi [lindex $argv 0]
opt_design
place_design
route_design
write_checkpoint -force [lindex $argv 1]
