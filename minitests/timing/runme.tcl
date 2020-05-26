# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
source $::env(XRAY_UTILS_DIR)/write_timing_info.tcl

proc create_design {design_name sig_mask verilogs} {
    create_project -part $::env(XRAY_PART) -force design_$design_name \
            design_$design_name

    foreach src $verilogs {
        read_verilog $src
    }
    synth_design -verilog_define SIG_MASK=$sig_mask -top top

    create_clock -period 10.000 -name clk -waveform {0.000 5.000} [get_ports clk]
    set_property -dict "PACKAGE_PIN W5 IOSTANDARD LVCMOS33" [get_ports clk]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports stb]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports di]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports do]

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

    if { $design_name == "fanout_ex_0" } {
        set_property FIXED_ROUTE "{ CLBLL_LL_D CLBLL_LL_DMUX }" [get_nets the_net]
    }

    place_design
    route_design

    write_checkpoint -force design_$design_name.dcp
    write_bitstream -force design_$design_name.bit
    save_project_as -force design_$design_name.xpr
}

proc run_timing {design_name sig_mask verilogs} {
    set name ${design_name}_${sig_mask}
    create_design $name $sig_mask $verilogs
    write_timing_info timing_$name.json5
}

run_timing $::env(DESIGN_NAME) $::env(ITER) $::env(VERILOGS)
