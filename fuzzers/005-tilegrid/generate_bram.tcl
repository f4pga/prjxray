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

    set selected_bram_sites {}
    set bram_index 0

    # LOC one BRAM (a "selected_lut") into each BRAM segment configuration column (ie 10 per CMT column)
    set bram_columns ""
    foreach bram $bram_bels {
        regexp "RAMB36_X([0-9]+)Y([0-9]+)/" $bram match slice_x slice_y

        # 10 per column => 10, 20, ,etc
        # ex: RAMB36_X0Y10/RAMBFIFO36E1
        set y_column [expr ($slice_y / 10) * 10]
        dict append bram_columns "X${slice_x}Y${y_column}" "$bram "
    }

    # Pick the smallest Y in each column.
    dict for {column brams_in_column} $bram_columns {
        set min_slice_y 9999999

        foreach bram $brams_in_column {
            regexp "RAMB36_X([0-9]+)Y([0-9]+)/" $bram match slice_x slice_y

            if { $slice_y < $min_slice_y } {
                set selected_bram_bel $bram
            }
        }

        set selected_bram_bel [get_bels $selected_bram_bel]

        set bram_site [get_sites -of_objects $selected_bram_bel]
        puts "LOCing BEL: $selected_bram_bel to $bram_site"
        set cell [get_cells roi/brams[$bram_index].bram]
        set_property LOC $bram_site $cell
        if {"$bram_site" == ""} {error "Bad site $bram_site from bel $selected_bram_bel"}

        set bram_index [expr $bram_index + 1]
        # Output site, not bel, to avoid reference issues after PnR
        lappend selected_bram_sites $bram_site
    }

    return $selected_bram_sites
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

