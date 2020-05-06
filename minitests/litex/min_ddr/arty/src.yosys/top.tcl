# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
proc write_iobuf_report {filename} {
    set fp [open $filename w]
    puts $fp "{ \"tiles\": \["
        foreach port [get_ports] {
            set net [get_nets -of $port]
            if { $net == "" } {
                continue
            }

            set cell [get_cells -of $net]
            set site [get_sites -of $cell]
            set tile [get_tiles -of $site]

            puts $fp "{"
                puts $fp "\"port\": \"$port\","
                puts $fp "\"pad_wire\": \"$net\","
                puts $fp "\"cell\": \"$cell\","
                puts $fp "\"site\": \"$site\","
                puts $fp "\"tile\": \"$tile\","
                puts $fp "\"type\": \"[get_property REF_NAME $cell]\","
                puts $fp "\"IOSTANDARD\": \"\\\"[get_property IOSTANDARD $cell]\\\"\","
                puts $fp "\"PULLTYPE\": \"\\\"[get_property PULLTYPE $cell]\\\"\","
                puts $fp "\"DRIVE\": \"[get_property DRIVE $cell]\","
                puts $fp "\"SLEW\": \"\\\"[get_property SLEW $cell]\\\"\","
            puts $fp "},"
        }
    puts $fp "\]}"
    close $fp
}

create_project -force -name top -part xc7a35ticsg324-1L
read_xdc ../top.xdc
read_edif ../top.edif
link_design -top top -part xc7a35ticsg324-1L
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
phys_opt_design
report_timing_summary -no_header -no_detailed_paths
write_checkpoint -force top_route.dcp
report_route_status -file top_route_status.rpt
report_drc -file top_drc.rpt
report_timing_summary -datasheet -max_paths 10 -file top_timing.rpt
report_power -file top_power.rpt
set_property BITSTREAM.CONFIG.SPI_BUSWIDTH 4 [current_design]
write_bitstream -force top.bit
write_cfgmem -force -format bin -interface spix4 -size 16 -loadbit "up 0x0 top.bit" -file top.bin

write_iobuf_report iobuf_report.json5


quit
