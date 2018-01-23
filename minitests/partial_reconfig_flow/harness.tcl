read_verilog top.v
read_verilog roi_base.v

synth_design -top top -part $::env(XRAY_PART)
write_checkpoint -force harness.dcp
