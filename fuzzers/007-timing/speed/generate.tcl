proc pin_info {pin} {
    set cell [get_cells -of_objects $pin]
    set bel [get_bels -of_objects $cell]
    set site [get_sites -of_objects $bel]
    return "$site $bel"
}

proc pin_bel {pin} {
    set cell [get_cells -of_objects $pin]
    set bel [get_bels -of_objects $cell]
    return $bel
}

proc build_design_full {} {
    create_project -force -part $::env(XRAY_PART) design design
    read_verilog ../top.v
    read_verilog ../../src/picorv32.v
    synth_design -top top

    #set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A5 I5:A6} \
            #	[get_cells -quiet -filter {REF_NAME == LUT6} -hierarchical]

    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports stb]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports di]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports do]

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

    set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]

    place_design
    route_design

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
}


proc build_design_synth {} {
    create_project -force -part $::env(XRAY_PART) design design

    read_verilog ../top.v
    read_verilog ../picorv32.v
    synth_design -top top
}

# WARNING: [Common 17-673] Cannot get value of property 'FORWARD' because this property is not valid in conjunction with other property setting on this object.
# WARNING: [Common 17-673] Cannot get value of property 'REVERSE' because this property is not valid in conjunction with other property setting on this object.
proc speed_models1 {} {
    set outdir "."
    set fp [open "$outdir/speed_model.txt" w]
    # list_property [lindex [get_speed_models] 0]
    set speed_models [get_speed_models]
    set properties [list_property [lindex $speed_models 0]]
    # "CLASS DELAY FAST_MAX FAST_MIN IS_INSTANCE_SPECIFIC NAME NAME_LOGICAL SLOW_MAX SLOW_MIN SPEED_INDEX TYPE"
    puts $fp $properties

    set needspace 0
    foreach speed_model $speed_models {
        foreach property $properties {
            if $needspace {
                puts -nonewline $fp " "
            }
            puts -nonewline $fp [get_property $property $speed_model]
            set needspace 1
        }
        puts $fp ""
    }
    close $fp
}

proc speed_models2 {} {
    set outdir "."
    set fp [open "$outdir/speed_model.txt" w]
    # list_property [lindex [get_speed_models] 0]
    set speed_models [get_speed_models]
    puts "Items: [llength $speed_models]"

    set needspace 0
    # Not all objects have the same properties
    # But they do seem to have the same list
    set properties [list_property [lindex $speed_models 0]]
    foreach speed_model $speed_models {
        set needspace 0
        foreach property $properties {
            set val [get_property $property $speed_model]
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


# For cost codes
# Items: 2663055s
# Hmm too much
# Lets filter out items we really want
proc nodes_all {} {
    set outdir "."
    set fp [open "$outdir/node_all.txt" w]
    set items [get_nodes]
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

# Only writes out items with unique cost codes
# (much faster)
proc nodes_unique_cc {} {
    set outdir "."
    set fp [open "$outdir/node.txt" w]
    set items [get_nodes]
    puts "Computing cost codes with [llength $items] items"

    set needspace 0
    set properties [list_property [lindex $items 0]]
    set cost_codes_known [dict create]
    set itemi 0
    foreach item $items {
        incr itemi
        set cost_code [get_property COST_CODE $item]
        if {[ dict exists $cost_codes_known $cost_code ]} {
            continue
        }
        puts "  Adding cost code $cost_code @ item $itemi"
        dict set cost_codes_known $cost_code 1

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

build_design_full
speed_models2
nodes_unique_cc
