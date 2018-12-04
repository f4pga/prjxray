source "$::env(FUZDIR)/util.tcl"

proc group_lut_cols { lut_bels } {
    # LOC one LUT (a "selected_lut") into each CLB segment configuration column (ie 50 per CMT column)
    set lut_columns ""
    foreach lut $lut_bels {
        regexp "SLICE_X([0-9]+)Y([0-9]+)/" $lut match slice_x slice_y

        # Only even SLICEs should be used as column bases.
        if { $slice_x % 2 != 0 } {
            continue
        }

        # 50 per column => 0, 50, 100, 150, etc
        # ex: SLICE_X2Y50/A6LUT
        # Only take one of the CLBs within a slice
        set y_column [expr ($slice_y / 50) * 50]
        dict append lut_columns "X${slice_x}Y${y_column}" "$lut "
    }
    return $lut_columns
}

proc loc_luts {} {
    set lut_bels [get_bels -of_objects [get_sites -of_objects [get_pblocks roi]] -filter {TYPE =~ LUT*} */A6LUT]
    set lut_columns [group_lut_cols $lut_bels]
    return [loc_dut_col_bels $lut_columns {roi/luts[} {].lut}]
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

