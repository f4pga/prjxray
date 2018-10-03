# General notes:
# Observed nets with 1 to 2 source cell pins
#   2 example
#   [get_pins -filter {DIRECTION == OUT} -of_objects $net]
#   roi/dout_shr[0]_i_1/O: BEL, visible
#   roi/dout_shr_reg[0]: no BEL, not visible, named after the net
#   I don't understand what the relationship between these two is
#   Maybe register retiming?
# Observed nets with 0 to 1 source bel pins
#   0 example: <const0>
# Recommendation: assume there is at most one source BEL
# Take that as the source BEL if it exists, otherwise don't do any source analysis

# get_timing_paths vs get_net_delays
# get_timing_paths is built on top of get_net_delays?
# has some different info, but is fixed on the slow max corner
# *possibly* reports slightly better info within a site, but would need to verify that

# Things safe to assume:
# -Each net has at least one delay?
# -Cell exists for every delay path
# -Each net has at least one destination BEL pin
# Things not safe to assume
# -Each net has at least one source BEL pin (ex: <const0>)


proc list_format {l delim} {
    set ret ""
    set needspace 0
    foreach x $l {
        if $needspace {
            set ret "$ret$delim$x"
        } else {
            set ret "$x"
        }
        set needspace 1
    }
    return $ret
}
proc write_info4 {} {
    set outdir "."
    set fp [open "$outdir/timing4.txt" w]
    # bel as site/bel, so don't bother with site
    puts $fp "linetype net src_site src_site_type src_site_pin src_bel src_bel_pin dst_site dst_site_type dst_site_pin dst_bel dst_bel_pin ico fast_max fast_min slow_max slow_min pips inodes wires"

    set TIME_start [clock clicks -milliseconds]
    set equations 0
    set nets_no_src_cell 0
    set nets_no_src_bel 0
    set lines_no_int 0
    set lines_some_int 0
    set neti 0
    set nets [get_nets -hierarchical]
    #set nets [get_nets clk]
    set nnets [llength $nets]
    foreach net $nets {
        incr neti

        puts "Net $neti / $nnets: $net"

        # there are some special places like on IOB where you may not have a cell source pin
        # this is due to special treatment where BEL vs SITE are blurred
        # The semantics of get_pins -leaf is kind of odd
        # When no passthrough LUTs exist, it has no effect
        # When passthrough LUT present:
        # -w/o -leaf: some pins + passthrough LUT pins
        # -w/ -leaf: different pins + passthrough LUT pins
        # With OUT filter this seems to be sufficient
        set src_cell_pins [get_pins -leaf -filter {DIRECTION == OUT} -of_objects $net]
        if {$src_cell_pins eq ""} {
            incr nets_no_src_cell
            # ex: IOB internal bel net
            puts "  SKIP: no source cell"
            continue
        }
        # 0 to 2 of these
        # Seems when 2 of them they basically have the same bel + cell
        # Make a best effort and move forward
        set src_cell_pin [lindex $src_cell_pins 0]
        set src_cell [get_cells -of_objects $src_cell_pin]

        # Only applicable if in a site
        set src_bel [get_bels -of_objects $src_cell]
        if {$src_bel eq ""} {
            # just throw out cases where source site doesn't exist
            # these are very special, don't really have timing info anyway
            # rework these later if they become problematic
            incr nets_no_src_bel
            puts "  SKIP: no source bel"
            continue
        }

        set src_bel_pin [get_bel_pins -of_objects $src_cell_pin]
        set src_site [get_sites -of_objects $src_bel]
        set src_site_type [get_property SITE_TYPE $src_site]
        # optional
        set src_site_pin [get_site_pins -of_objects $src_cell_pin]

        # Report delays with and without interconnect only
        foreach ico "0 1" {
            if $ico {
                set delays [get_net_delays -interconnect_only -of_objects $net]
            } else {
                set delays [get_net_delays -of_objects $net]
                # only increment on one of the paths
                set equations [expr "$equations + [llength $delays]"]
            }
            puts $fp "GROUP $ico [llength $delays]"
            foreach delay $delays {
                #set delaystr [get_property NAME $delay]

                set fast_max [get_property "FAST_MAX" $delay]
                set fast_min [get_property "FAST_MIN" $delay]
                set slow_max [get_property "SLOW_MAX" $delay]
                set slow_min [get_property "SLOW_MIN" $delay]

                # Does this always exist?
                set dst_cell_pin_str [get_property TO_PIN $delay]
                set dst_cell_pin [get_pins $dst_cell_pin_str]
                set dst_cell [get_cells -of_objects $dst_cell_pin]
                set dst_bel [get_bels -of_objects $dst_cell]
                set dst_bel_pin [get_bel_pins -of_objects $dst_cell_pin]
                set dst_site [get_sites -of_objects $dst_bel]
                set dst_site_type [get_property SITE_TYPE $dst_site]
                # optional
                set dst_site_pin [get_site_pins -of_objects $dst_cell_pin]

                # No fabric on this net?
                # don't try querying sites and such
                if {[get_nodes -of_objects $net] eq ""} {
                    # Already have everything we could query
                    # Just output
                    incr lines_no_int
                    puts $fp "NET $net $src_site $src_site_type $src_site_pin $src_bel $src_bel_pin $dst_site $dst_site_type $dst_site_pin $dst_bel $dst_bel_pin $ico $fast_max $fast_min $slow_max $slow_min $pips_out $nodes_out $wires_out"
                # At least some fabric exists
                # Does dest BEL exist but not source BEL?
                } elseif {$src_bel eq ""} {
                    puts "ERROR: should have been filtered"
                    return
                # Ideally query from and to cell pins
                } else {
                    # Nested list delimination precedence: " |:"

                    # Pips in between
                    # Walk net, looking for interesting elements in between
                    #  -from <args> - (Optional) Defines the starting points of the pips to get
                    #  from wire or site_pin
                    set pips [get_pips -of_objects $net -from $src_site_pin -to $dst_site_pin]
                    # Write pips w/ speed index
                    foreach pip $pips {
                        set speed_index [get_property SPEED_INDEX $pip]
                        lappend pips_out "$pip:$speed_index"
                    }
                    set pips_out [list_format "$pips_out" "|"]

                    # Write nodes
                    # XXX: remove? don't think I care about these
                    # most for debugging at this point
                    set nodes [get_nodes -of_objects $net -from $src_site_pin -to $dst_site_pin]
                    if {$nodes eq ""} {
                        puts "ERROR: no nodes"
                        return
                    }
                    foreach node $nodes {
                        set nwires [llength [get_wires -of_objects $node]]
                        lappend nodes_out "$node:$nwires"
                    }
                    set nodes_out [list_format "$nodes_out" "|"]

                    set wires [get_wires -of_objects $nodes]
                    # Write wires
                    foreach wire $wires {
                        set speed_index [get_property SPEED_INDEX $wire]
                        lappend wires_out "$wire:$speed_index"
                    }
                    set wires_out [list_format "$wires_out" "|"]

                    incr lines_some_int
                    puts $fp "NET $net $src_site $src_site_type $src_site_pin $src_bel $src_bel_pin $dst_site $dst_site_type $dst_site_pin $dst_bel $dst_bel_pin $ico $fast_max $fast_min $slow_max $slow_min $pips_out $nodes_out $wires_out"
                }
            }
        }
    }
    close $fp
    set TIME_taken [expr [clock clicks -milliseconds] - $TIME_start]
    puts "Took ms: $TIME_taken"
    puts "Generated $equations equations"
    puts "Nets: $nnets"
    puts "  Skipped (no source cell): $nets_no_src_cell"
    puts "  Skipped (no source bel): $nets_no_src_bel"
    puts "Lines"
    puts "  No interconnect: $lines_no_int"
    puts "  Has interconnect: $lines_some_int"
}

