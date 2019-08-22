create_project -force -part xc7a35ticsg324-1L $::env(TESTBENCH_TITLE) $::env(TESTBENCH_TITLE)

read_verilog $::env(TESTBENCH_TITLE).v

set_property top tb [get_filesets sim_1]

synth_design -top tb -verbose

set_property xsim.simulate.log_all_signals true [get_filesets sim_1]
set_property xsim.simulate.runtime 0 [get_filesets sim_1]

launch_simulation -verbose
restart

open_vcd ../../../../waveforms.vcd

run -all

flush_vcd
close_vcd

