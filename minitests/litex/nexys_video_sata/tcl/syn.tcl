# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
create_project -force -name $env(PROJECT_NAME) -part $env(XRAY_PART)

read_verilog ../build/nexys_video/gateware/nexys_video.v $env(VIRTUAL_ENV)/src/pythondata-cpu-vexriscv/pythondata_cpu_vexriscv/verilog/VexRiscv.v

synth_design -top nexys_video -max_dsp 0

report_timing_summary -file top_timing_synth.rpt
report_utilization -hierarchical -file top_utilization_hierarchical_synth.rpt
report_utilization -file top_utilization_synth.rpt

write_edif -force ../$env(PROJECT_NAME).edif
