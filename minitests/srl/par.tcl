# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
create_project -force -name $env(PROJECT_NAME) -part xc7a35ticsg324-1L

#read_xdc ../top.xdc
read_edif ../$env(PROJECT_NAME).edif

link_design -part xc7a35ticsg324-1L

report_timing_summary -file top_timing_synth.rpt
report_utilization -hierarchical -file top_utilization_hierarchical_synth.rpt
report_utilization -file top_utilization_synth.rpt

opt_design
place_design

report_utilization -hierarchical -file top_utilization_hierarchical_place.rpt
report_utilization -file top_utilization_place.rpt
report_io -file top_io.rpt
report_control_sets -verbose -file top_control_sets.rpt
report_clock_utilization -file top_clock_utilization.rpt

route_design
#phys_opt_design

report_timing_summary -no_header -no_detailed_paths

write_checkpoint -force ../$env(PROJECT_NAME).dcp

set_property SEVERITY {Warning} [get_drc_checks UCIO-1]
set_property SEVERITY {Warning} [get_drc_checks NSTD-1]

report_route_status -file top_route_status.rpt
report_drc -file top_drc.rpt
report_timing_summary -datasheet -max_paths 10 -file top_timing.rpt
report_power -file top_power.rpt

write_bitstream -force ../$env(PROJECT_NAME).bit
