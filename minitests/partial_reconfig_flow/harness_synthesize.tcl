read_verilog harness.v
synth_design -top top -part $::env(XRAY_PART)
write_checkpoint -force harness_synth.dcp
