proc write_timing_info {filename} {
    set fp [open $filename w]
    puts $fp "\["

    set nets [get_nets]
    foreach net $nets {
        if { $net == "<const0>" || $net == "<const1>" } {
            continue
        }

        if { [get_property ROUTE_STATUS [get_nets $net]] == "INTRASITE" } {
            continue
        }
        if { [get_property ROUTE_STATUS [get_nets $net]] == "NOLOADS" } {
            continue
        }

        puts $fp "{"
            puts $fp "\"net\":\"$net\","

            set route [get_property ROUTE $net]
            puts $fp "\"route\":\"$route\","

            set pips [get_pips -of_objects $net]
            puts $fp "\"pips\":\["
            foreach pip $pips {
                puts $fp "{"
                    puts $fp "\"name\":\"$pip\","
                    puts $fp "\"src_wire\":\"[get_wires -uphill -of_objects $pip]\","
                    puts $fp "\"dst_wire\":\"[get_wires -downhill -of_objects $pip]\","
                    puts $fp "\"speed_index\":\"[get_property SPEED_INDEX $pip]\","
                    puts $fp "\"is_directional\":\"[get_property IS_DIRECTIONAL  $pip]\","
                puts $fp "},"
            }
            puts $fp "\],"
            puts $fp "\"nodes\":\["
            set nodes [get_nodes -of_objects $net]
            foreach node $nodes {
                puts $fp "{"
                    puts $fp "\"name\":\"$node\","
                    puts $fp "\"cost_code\":\"[get_property COST_CODE $node]\","
                    puts $fp "\"cost_code_name\":\"[get_property COST_CODE_NAME $node]\","
                    puts $fp "\"speed_class\":\"[get_property SPEED_CLASS $node]\","
                    puts $fp "\"wires\":\["
                    set wires [get_wires -of_objects $node]
                    foreach wire $wires {
                        puts $fp "{"
                            puts $fp "\"name\":\"$wire\","
                            puts $fp "\"cost_code\":\"[get_property COST_CODE $wire]\","
                            puts $fp "\"speed_index\":\"[get_property SPEED_INDEX $wire]\","
                        puts $fp "},"
                    }
                    puts $fp "\],"
                puts $fp "},"
            }
            puts $fp "\],"

            set opin [get_pins -leaf -of_objects [get_nets $net] -filter {DIRECTION == OUT}]
            puts $fp "\"opin\": {"
                puts $fp "\"name\":\"$opin\","
                set opin_site_pin [get_site_pins -of_objects $opin]
                puts $fp "\"site_pin\":\"$opin_site_pin\","
                puts $fp "\"site_pin_speed_index\":\"[get_property SPEED_INDEX $opin_site_pin]\","
                puts $fp "\"node\":\"[get_nodes -of_objects $opin_site_pin]\","
                puts $fp "\"wire\":\"[get_wires -of_objects [get_nodes -of_objects $opin_site_pin]]\","
            puts $fp "},"
            set ipins [get_pins -of_objects [get_nets $net] -filter {DIRECTION == IN} -leaf]
            puts $fp "\"ipins\":\["
            foreach ipin $ipins {
                puts $fp "{"
                    set delay [get_net_delays -interconnect_only -of_objects $net -to $ipin]
                    puts $fp "\"name\":\"$ipin\","
                    puts $fp "\"ic_delays\":{"
                        foreach prop {"FAST_MAX" "FAST_MIN" "SLOW_MAX" "SLOW_MIN"} {
                            puts $fp "\"$prop\":\"[get_property $prop $delay]\","
                        }
                    puts $fp "},"
                    set ipin_site_pin [get_site_pin -of_objects $ipin]
                    puts $fp "\"site_pin\":\"$ipin_site_pin\","
                    puts $fp "\"site_pin_speed_index\":\"[get_property SPEED_INDEX $ipin_site_pin]\","
                    puts $fp "\"node\":\"[get_nodes -of_objects $ipin_site_pin]\","
                    puts $fp "\"wire\":\"[get_wires -of_objects [get_nodes -of_objects $ipin_site_pin]]\","
                puts $fp "},"
            }
            puts $fp "\],"

        puts $fp "},"
    }

    puts $fp "\]"
    close $fp
}

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
