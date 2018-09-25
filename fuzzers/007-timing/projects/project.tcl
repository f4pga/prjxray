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

# Changed to group wires and nodes
# This allows tracing the full path along with pips
proc write_info3 {} {
    set outdir "."
    set fp [open "$outdir/timing4.txt" w]
    # bel as site/bel, so don't bother with site
    puts $fp "linetype net src_site src_site_pin src_bel src_bel_pin dst_site dst_site_pin dst_bel dst_bel_pin ico fast_max fast_min slow_max slow_min pips inodes wires"

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
        set src_bel_pin [get_bel_pins -of_objects $src_pin]
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
                puts $fp "GROUP $ico [llength $delays]"
                foreach delay $delays {
                    set delaystr [get_property NAME $delay]
                    set dst_pins [get_property TO_PIN $delay]
                    set dst_pin [get_pins $dst_pins]
                    #puts "  $delaystr: $src_pin => $dst_pin"
                    set dst_bel [pin_bel $dst_pin]
                    set dst_bel_pin [get_bel_pins -of_objects $dst_pin]
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

                        puts -nonewline $fp "NET $net $src_site $src_site_pin $src_bel $src_bel_pin $dst_site $dst_site_pin $dst_bel $dst_bel_pin $ico $fast_max $fast_min $slow_max $slow_min"
        
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

