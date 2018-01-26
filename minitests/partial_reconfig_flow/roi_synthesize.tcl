read_verilog [lindex $argv 0]
synth_design -mode out_of_context -top roi -part $::env(XRAY_PART)
write_checkpoint -force [lindex $argv 1]

