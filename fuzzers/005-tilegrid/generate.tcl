proc make_project {} {
    create_project -force -part $::env(XRAY_PART) design design

    read_verilog ../top.v
    synth_design -top top

    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports di]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports do]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports stb]

    create_pblock roi
    add_cells_to_pblock [get_pblocks roi] [get_cells roi]
    resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
    set_param tcl.collectionResultDisplayLimit 0

    set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]
}

proc loc_luts {} {
    set luts [get_bels -of_objects [get_sites -of_objects [get_pblocks roi]] -filter {TYPE =~ LUT*} */A6LUT]
    set selected_luts {}
    set lut_index 0

    # LOC one LUT (a "selected_lut") into each CLB segment configuration column (ie 50 per CMT column)
    foreach lut $luts {
        set tile [get_tile -of_objects $lut]
        set grid_x [get_property GRID_POINT_X $tile]
        set grid_y [get_property GRID_POINT_Y $tile]

        # 50 per column => 50, 100, 150, etc
        # ex: SLICE_X2Y50/A6LUT
        # Only take one of the CLBs within a slice
        if [regexp "X.*[02468]Y.*[05]0/" $lut] {
            set cell [get_cells roi/luts[$lut_index].lut]
            set_property LOC [get_sites -of_objects $lut] $cell
            set lut_index [expr $lut_index + 1]
            lappend selected_luts $lut
        }
    }
    return $selected_luts
}

proc loc_brams {} {
    # XXX: for some reason this doesn't work if there is a cell already there
    # but LUTs don't have this issue
    set brams [get_bels -of_objects [get_sites -of_objects [get_pblocks roi]] -filter {TYPE =~ RAMBFIFO36E1*}]
    set selected_brams {}
    set bram_index 0

    # LOC one BRAM (a "selected_lut") into each BRAM segment configuration column (ie 10 per CMT column)
    foreach bram $brams {
        set tile [get_tile -of_objects $bram]
        set grid_x [get_property GRID_POINT_X $tile]
        set grid_y [get_property GRID_POINT_Y $tile]

        # 10 per column => 10, 20, ,etc
        # ex: RAMB36_X0Y10/RAMBFIFO36E1
        if [regexp "Y.*0/" $bram] {
            set cell [get_cells roi/brams[$bram_index].bram]
            set_property LOC [get_sites -of_objects $bram] $cell
            set bram_index [expr $bram_index + 1]
            lappend selected_brams $bram
        }
    }
    return $selected_brams
}

proc write_tiles_txt {} {
    # Get all tiles, ie not just the selected LUTs
    set tiles [get_tiles]

    # Write tiles.txt with site metadata
    set fp [open "tiles.txt" w]
    foreach tile $tiles {
        set type [get_property TYPE $tile]
        set grid_x [get_property GRID_POINT_X $tile]
        set grid_y [get_property GRID_POINT_Y $tile]
        set sites [get_sites -quiet -of_objects $tile]
        set typed_sites {}

        if [llength $sites] {
            set site_types [get_property SITE_TYPE $sites]
            foreach t $site_types s $sites {
                lappend typed_sites $t $s
            }
        }

        puts $fp "$type $tile $grid_x $grid_y $typed_sites"
    }
    close $fp
}

proc write_clbs { selected_luts } {
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
        write_bitstream -force design_[get_sites -of_objects [lindex $selected_luts $i]].bit
        set_property INIT $orig_init $cell
    }
}

proc write_brams { selected_brams } {
    # Toggle one bit in each selected BRAM to generate base addresses
    for {set i 0} {$i < [llength $selected_brams]} {incr i} {
        puts ""
        set cell [get_cells roi/brams[$i].bram]
        puts "BRAM $cell"
        set orig_init [get_property INIT_00 $cell]
        # Flip a bit by changing MSB 0 => 1
        set new_init [regsub "h8" $orig_init "h0"]
        puts "INIT_00 $orig_init => $new_init"
        set_property INIT_00 $new_init $cell
        write_bitstream -force design_[get_sites -of_objects [lindex $selected_brams $i]].bit
        set_property INIT_00 $orig_init $cell
    }
}

proc run {} {
    make_project
    set selected_luts [loc_luts]
    puts "Selected LUTs: [llength $selected_luts]"
    set selected_brams [loc_brams]
    puts "Selected LUTs: [llength $selected_brams]"

    place_design
    route_design
    write_checkpoint -force design.dcp
    write_bitstream -force design.bit

    write_tiles_txt
    write_clbs $selected_luts
    write_brams $selected_brams
}

run

