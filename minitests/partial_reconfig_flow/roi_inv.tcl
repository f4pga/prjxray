read_verilog roi_inv.v
synth_design -mode out_of_context -top roi -part $::env(XRAY_PART)
write_checkpoint -force roi_inv.dcp
