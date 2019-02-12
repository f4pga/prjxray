source "$::env(XRAY_DIR)/utils/utils.tcl"

proc write_route_data {filename} {
    set fp [open $filename w]
    foreach net [get_nets -hierarchical] {
        puts $fp "Net $net route:"
        puts $fp [report_route_status -of_objects $net -return_string]
        puts $fp ""
    }
    close $fp
}

proc run {} {
    create_project -force -part $::env(XRAY_PART) design design
    read_verilog top.v
    synth_design -top top

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

    place_design
    route_design

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
    write_route_data design.txt
}

run
