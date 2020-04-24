source "$::env(XRAY_DIR)/utils/utils.tcl"

proc write_pip_txtdata {filename} {
    puts "FUZ([pwd]): Writing $filename."
    set fp [open $filename w]
    set nets [get_nets -hierarchical]
    set nnets [llength $nets]
    set neti 0
    foreach net $nets {
        incr neti
        if {($neti % 100) == 0 } {
            puts "FUZ([pwd]): Dumping pips from net $net ($neti / $nnets)"
        }
        foreach pip [get_pips -of_objects $net] {
            set tile [get_tiles -of_objects $pip]
            set src_wire [get_wires -uphill -of_objects $pip]
            set dst_wire [get_wires -downhill -of_objects $pip]
            set num_pips [llength [get_nodes -uphill -of_objects [get_nodes -of_objects $dst_wire]]]
            set dir_prop [get_property IS_DIRECTIONAL $pip]
            puts $fp "$tile $pip $src_wire $dst_wire $num_pips $dir_prop"
        }
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
    set_property IS_ENABLED 0 [get_drc_checks {AVAL-74}]
    set_property IS_ENABLED 0 [get_drc_checks {PDRC-26}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-4}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-5}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-13}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-98}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-99}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-105}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-115}]
    set_property IS_ENABLED 0 [get_drc_checks {REQP-144}]

    set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets]

    place_design -directive Quick
    write_checkpoint -force design_before_route.dcp
    route_design -directive Quick
    write_checkpoint -force design.dcp

    write_bitstream -force design.bit
    write_pip_txtdata design.txt
}

run
