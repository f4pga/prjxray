source ../../../../utils/utils.tcl

proc build_design {} {
    create_project -force -part $::env(XRAY_PART) design design
    read_verilog ../../src/picorv32.v
    read_verilog ../top.v
    synth_design -top top

    puts "Locking pins"
    set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A5 I5:A6} \
            [get_cells -quiet -filter {REF_NAME == LUT6} -hierarchical]

    puts "Package stuff"
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports stb]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports di]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports do]

    puts "pblocking"
    create_pblock roi
    set roipb [get_pblocks roi]
    add_cells_to_pblock $roipb [get_cells roi]
    resize_pblock $roipb -add "$::env(XRAY_ROI)"

    puts "randplace"
    randplace_pblock 50 roi

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

    puts "dedicated route"
    set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]

    place_design
    route_design

    write_checkpoint -force design.dcp
    # disable combinitorial loop
    # set_property IS_ENABLED 0 [get_drc_checks {LUTLP-1}]
    #write_bitstream -force design.bit
}

proc pips_all {} {
    set outdir "."
    set fp [open "$outdir/pip_all.txt" w]
    set items [get_pips]
    puts "Items: [llength $items]"

    set needspace 0
    set properties [list_property [lindex $items 0]]
    foreach item $items {
        set needspace 0
        foreach property $properties {
            set val [get_property $property $item]
            if {"$val" ne ""} {
                if $needspace {
                    puts -nonewline $fp " "
                }
                puts -nonewline $fp "$property:$val"
                set needspace 1
            }
        }
        puts $fp ""
    }
    close $fp
}
proc wires_all {} {
    set outdir "."
    set fp [open "$outdir/wire_all.txt" w]
    set items [get_wires]
    puts "Items: [llength $items]"

    set needspace 0
    set properties [list_property [lindex $items 0]]
    foreach item $items {
        set needspace 0
        foreach property $properties {
            set val [get_property $property $item]
            if {"$val" ne ""} {
                if $needspace {
                    puts -nonewline $fp " "
                }
                puts -nonewline $fp "$property:$val"
                set needspace 1
            }
        }
        puts $fp ""
    }
    close $fp
}

build_design
pips_all
wires_all
