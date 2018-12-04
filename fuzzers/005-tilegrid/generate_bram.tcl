source "$::env(FUZDIR)/util.tcl"

# Return a list of sites containing BRAMs
# sites are better than bels because site type may change and invalidate the bel
proc loc_brams {} {
    # BRAM have multiple mutually exclusive sites
    # They can be cycled by setting the site type
    # Ex:
    # - RAMB36_X0Y10/RAMBFIFO36E1
    # - RAMB36_X0Y10/RAMB36E1
    # Default is RAMBFIFO36E1?
    # Work primarily on sites, not bels,
    # to avoid issues when switching site type during PnR
    set bram_sites [get_sites -of_objects [get_pblocks roi] -filter {SITE_TYPE =~ RAMBFIFO36E1*}]
    set bram_bels [get_bels -of_objects $bram_sites]

    set bram_columns [group_dut_cols $bram_bels 10]
    # Output site, not bel, to avoid reference issues after PnR
    return [loc_dut_col_sites $bram_columns {roi/brams[} {].bram}]
}

proc write_brams { selected_brams_sites } {
    puts "write_brams: [llength $selected_brams_sites] BRAMs"
    puts ""
    # Toggle one bit in each selected BRAM to generate base addresses
    for {set i 0} {$i < [llength $selected_brams_sites]} {incr i} {
        puts ""
        set cell [get_cells roi/brams[$i].bram]
        puts "BRAM $cell"
        set orig_init [get_property INIT_00 $cell]
        # Flip a bit by changing MSB 0 => 1
        set new_init [regsub "h8" $orig_init "h0"]
        puts "INIT_00 $orig_init => $new_init"
        set_property INIT_00 $new_init $cell
        set site [lindex $selected_brams_sites $i]
        if {"$site" == ""} {error "Bad site $site"}
        write_bitstream -force design_$site.bit
        set_property INIT_00 $orig_init $cell
    }
}

proc run {} {
    make_project
    set selected_brams_sites [loc_brams]
    puts "Selected BRAMs: [llength $selected_brams_sites]"

    place_design
    route_design
    write_checkpoint -force design.dcp
    write_bitstream -force design.bit

    write_brams $selected_brams_sites
}

run

