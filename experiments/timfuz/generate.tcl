source ../../../utils/utils.tcl

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

proc build_design {} {
    create_project -force -part $::env(XRAY_PART) design design
    #read_verilog ../top.v
    #read_verilog ../picorv32.v
    #read_verilog ../oneblinkw.v
    read_verilog placelut.v
    synth_design -top top

    puts "Locking pins"
    set_property LOCK_PINS {I0:A1 I1:A2 I2:A3 I3:A4 I4:A5 I5:A6} \
		[get_cells -quiet -filter {REF_NAME == LUT6} -hierarchical]

    puts "Package stuff"
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports stb]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports di]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports do]

    if {0 < 0} {
        puts "pblocking"
        create_pblock roi
        set roipb [get_pblocks roi]
        set_property EXCLUDE_PLACEMENT 1 $roipb
        add_cells_to_pblock $roipb [get_cells roi]
        resize_pblock $roipb -add "$::env(XRAY_ROI)"

        puts "randplace"
        randplace_pblock 150 $roipb
    }

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

# Changed to group wires and nodes
# This allows tracing the full path along with pips
proc write_info3 {} {
    set outdir "."
    set fp [open "$outdir/timing3.txt" w]
    # bel as site/bel, so don't bother with site
    puts $fp "net src_bel dst_bel ico fast_max fast_min slow_max slow_min pips inodes wires"

    set TIME_start [clock clicks -milliseconds]
    set verbose 0
    set equations 0
    set site_src_nets 0
    set site_dst_nets 0
    set neti 0
    set nets [get_nets -hierarchical]
    set nnets [llength $nets]
    foreach net $nets {
        incr neti
        #if {$neti >= 10} {
        #    puts "Debug break"
        #    break
        #}

        puts "Net $neti / $nnets: $net"
        # The semantics of get_pins -leaf is kind of odd
        # When no passthrough LUTs exist, it has no effect
        # When passthrough LUT present:
        # -w/o -leaf: some pins + passthrough LUT pins
        # -w/ -leaf: different pins + passthrough LUT pins
        # With OUT filter this seems to be sufficient
        set src_pin [get_pins -leaf -filter {DIRECTION == OUT} -of_objects $net]
        set src_bel [pin_bel $src_pin]
        set src_site [get_sites -of_objects $src_bel]
        # Only one net driver
        set src_site_pins [get_site_pins -filter {DIRECTION == OUT} -of_objects $net]

        # Sometimes this is empty for reasons that escape me
        # Emitting direction doesn't help
        if {[llength $src_site_pins] < 1} {
            if $verbose {
                puts "    Ignoring site internal net"
            }
            incr site_src_nets
            continue
        }
        set dst_site_pins_net [get_site_pins -filter {DIRECTION == IN} -of_objects $net]
        if {[llength $dst_site_pins_net] < 1} {
            puts "  Skipping site internal source net"
            incr site_dst_nets
            continue
        }
        foreach src_site_pin $src_site_pins {
            if $verbose {
                puts "Source: $src_pin at site $src_site:$src_bel, spin $src_site_pin"
            }

            # Run with and without interconnect only
            foreach ico "0 1" {
                set ico_flag ""
                if $ico {
                    set ico_flag "-interconnect_only"
                    set delays [get_net_delays $ico_flag -of_objects $net]
                } else {
                    set delays [get_net_delays -of_objects $net]
                }
                foreach delay $delays {
                    set delaystr [get_property NAME $delay]
                    set dst_pins [get_property TO_PIN $delay]
                    set dst_pin [get_pins $dst_pins]
                    #puts "  $delaystr: $src_pin => $dst_pin"
                    set dst_bel [pin_bel $dst_pin]
                    set dst_site [get_sites -of_objects $dst_bel]
                    if $verbose {
                        puts "  Dest: $dst_pin at site $dst_site:$dst_bel"
                    }

                    set dst_site_pins [get_site_pins -of_objects $dst_pin]
                    # Some nets are internal
                    # But should this happen on dest if we've already filtered source?
                    if {"$dst_site_pins" eq ""} {
                        continue
                    }
                    # Also apparantly you can have multiple of these as well
                    foreach dst_site_pin $dst_site_pins {
                        set fast_max [get_property "FAST_MAX" $delay]
                        set fast_min [get_property "FAST_MIN" $delay]
                        set slow_max [get_property "SLOW_MAX" $delay]
                        set slow_min [get_property "SLOW_MIN" $delay]

                        # Want:
                        # Site / BEL at src
                        # Site / BEL at dst
                        # Pips in between
                        # Walk net, looking for interesting elements in between
                        set pips [get_pips -of_objects $net -from $src_site_pin -to $dst_site_pin]
                        if $verbose {
                            foreach pip $pips {
                                puts "    PIP $pip"
                            }
                        }
                        set nodes [get_nodes -of_objects $net -from $src_site_pin -to $dst_site_pin]
                        #set wires [get_wires -of_objects $net -from $src_site_pin -to $dst_site_pin]
                        set wires [get_wires -of_objects $nodes]

                        # puts $fp "$net $src_bel $dst_bel $ico $fast_max $fast_min $slow_max $slow_min $pips"
                        puts -nonewline $fp "$net $src_bel $dst_bel $ico $fast_max $fast_min $slow_max $slow_min"
        
                        # Write pips w/ speed index
                        puts -nonewline $fp " "
                        set needspace 0
                        foreach pip $pips {
                            if $needspace {
                                puts -nonewline $fp "|"
                            }
                            set speed_index [get_property SPEED_INDEX $pip]
                            puts -nonewline $fp "$pip:$speed_index"
                            set needspace 1
                        }

                        # Write nodes
                        #set nodes_str [string map {" " "|"} $nodes]
                        #puts -nonewline $fp " $nodes_str"
                        puts -nonewline $fp " "
                        set needspace 0
                        foreach node $nodes {
                            if $needspace {
                                puts -nonewline $fp "|"
                            }
                            set nwires [llength [get_wires -of_objects $node]]
                            puts -nonewline $fp "$node:$nwires"
                            set needspace 1
                        }

                        # Write wires
                        puts -nonewline $fp " "
                        set needspace 0
                        foreach wire $wires {
                            if $needspace {
                                puts -nonewline $fp "|"
                            }
                            set speed_index [get_property SPEED_INDEX $wire]
                            puts -nonewline $fp "$wire:$speed_index"
                            set needspace 1
                        }

                        puts $fp ""

                        incr equations
                        break
                    }
                }
            }
        }
    }
    close $fp
    set TIME_taken [expr [clock clicks -milliseconds] - $TIME_start]
    puts "Took ms: $TIME_taken"
    puts "Generated $equations equations"
    puts "Skipped $site_src_nets (+ $site_dst_nets) site nets"
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
#write_info2
write_info3
#wires_all
#pips_all

