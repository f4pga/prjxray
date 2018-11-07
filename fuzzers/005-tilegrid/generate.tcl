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
    foreach roi "$::env(XRAY_ROI)" {
        puts "ROI: $roi"
        resize_pblock [get_pblocks roi] -add "$roi"
    }

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
    set selected_luts [loc_luts]
    puts "Selected LUTs: [llength $selected_luts]"
    set selected_brams_sites [loc_brams]
    puts "Selected BRAMs: [llength $selected_brams_sites]"

    place_design
    route_design
    write_checkpoint -force design.dcp
    write_bitstream -force design.bit

    write_tiles_txt
    write_clbs $selected_luts
    write_brams $selected_brams_sites
}

run

