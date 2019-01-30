proc run {} {
    create_project -force -part $::env(XRAY_PART) design design
    read_verilog top.v
    synth_design -top top

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
    set_property IS_ENABLED 0 [get_drc_checks {PDCN-137}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-191}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-192}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-193}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-194}]

    place_design
    route_design

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
}

run
