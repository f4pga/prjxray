source "$::env(FUZDIR)/util.tcl"

# FIXME: change to grab one IOB from each column
proc loc_iob_old {} {
    set ports [concat [get_ports clk] [get_ports do] [get_ports stb] [get_ports di]]
    set selected_iobs {}
    foreach port $ports {
        set site [get_sites -of_objects $port]
        set tile [get_tiles -of_objects $site]
        set grid_x [get_property GRID_POINT_X $tile]
        set grid_y [get_property GRID_POINT_Y $tile]
         # 50 per column => 50, 100, 150, etc
        if [regexp "Y(?:.*[05])?0" $site] {
            lappend selected_iobs $port
        }
    }
    return $selected_iobs
}

proc loc_iob {} {
    # Get all possible sites
    set duts [make_iob_sites]
    # Sort them into CMT columns
    set dut_columns [group_dut_cols $duts 75]
    # Assign one from each
    return [loc_dut_col_bels $dut_columns {di[} {]} ]
}

proc write_iob { selected_iobs } {
    foreach port $selected_iobs {
      puts ""
      set site [get_sites -of_objects $port]
      set tile [get_tiles -of_objects $site]
      set pin [get_property PACKAGE_PIN $port]
      puts "IOB33 $port $site $tile $pin"
      set orig_init [get_property PULLTYPE $port]
      set_property PULLTYPE PULLUP $port
      write_bitstream -force design_$site.bit
      set_property PULLTYPE "$orig_init" $port
    }
}

proc run {} {
    make_project
    set selected_iobs [loc_iob]
    puts "Selected IOBs: [llength $selected_iobs]"

    place_design
    route_design
    write_checkpoint -force design.dcp
    write_bitstream -force design.bit

    write_iob $selected_iobs
}

run

