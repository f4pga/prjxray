source "$::env(FUZDIR)/util.tcl"

proc loc_luts {} {
    set luts [get_bels -of_objects [get_sites -of_objects [get_pblocks roi]] -filter {TYPE =~ LUT*} */A6LUT]
    set selected_luts {}
    set lut_index 0

    # LOC one LUT (a "selected_lut") into each CLB segment configuration column (ie 50 per CMT column)
    set lut_columns ""
    foreach lut $luts {
        regexp "SLICE_X([0-9]+)Y([0-9]+)/" $lut match slice_x slice_y

        # Only even SLICEs should be used as column bases.
        if { $slice_x % 2 != 0 } {
            continue
        }

        # 50 per column => 50, 100, 150, etc
        # ex: SLICE_X2Y50/A6LUT
        # Only take one of the CLBs within a slice
        set y_column [expr ($slice_y / 50) * 50]
        dict append lut_columns "X${slice_x}Y${y_column}" "$lut "
    }

    # Pick the smallest Y in each column.
    dict for {column luts_in_column} $lut_columns {
        set min_slice_y 9999999

        foreach lut $luts_in_column {
            regexp "SLICE_X([0-9]+)Y([0-9]+)/" $lut slice_x slice_y

            if { $slice_y < $min_slice_y } {
                set selected_lut $lut
            }
        }

        set cell [get_cells roi/luts[$lut_index].lut]
        set lut_site [get_sites -of_objects [get_bels $selected_lut]]
        puts "LOCing $selected_lut to $lut_site"
        set_property LOC $lut_site $cell
        set lut_index [expr $lut_index + 1]
        lappend selected_luts [get_bels $selected_lut]
    }

    return $selected_luts
}

proc write_clbs { selected_luts } {
    puts "write_brams: [llength $selected_luts] LUTs"
    puts ""
    # Toggle one bit in each selected LUT to generate base addresses
    for {set i 0} {$i < [llength $selected_luts]} {incr i} {
        puts ""
        set cell [get_cells roi/luts[$i].lut]
        puts "LUT $cell"
        set orig_init [get_property INIT $cell]
        # Flip a bit by changing MSB 0 => 1
        set new_init [regsub "h8" $orig_init "h0"]
        puts "INIT $orig_init => $new_init"
        set_property INIT $new_init $cell
        set site [get_sites -of_objects [lindex $selected_luts $i]]
        write_bitstream -force design_$site.bit
        set_property INIT $orig_init $cell
    }
}

proc run {} {
    make_project
    set selected_luts [loc_luts]
    puts "Selected LUTs: [llength $selected_luts]"

    place_design
    route_design
    write_checkpoint -force design.dcp
    write_bitstream -force design.bit

    write_clbs $selected_luts
}

run

