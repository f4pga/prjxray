source "$::env(FUZDIR)/util.tcl"

proc loc_iob {} {
    # Some pads are output only (ex: OPAD_X0Y0/PAD) => filt IOB_*
    # XXX: GTX bank missing, deal with that later
    set roi_sites [get_sites -of_objects [get_pblocks roi]]
    set duts [get_bels -of_objects $roi_sites -filter {TYPE =~ PAD && NAME =~ IOB_*}]

    # Sort them into CMT columns
    set dut_columns [group_dut_cols $duts 50]
    # Assign one from each
    return [loc_dut_col_sites $dut_columns {di_bufs[} {].ibuf} ]
}

proc write_iob { sel_iob_sites } {
    foreach site $sel_iob_sites {
        puts ""
        set port [get_ports -of_objects $site]
        set tile [get_tiles -of_objects $site]
        set pin [get_property PACKAGE_PIN $port]
        puts "IOB $port $site $tile $pin"
        set orig_init [get_property PULLTYPE $port]
        set_property PULLTYPE PULLUP $port
        write_bitstream -force design_$site.bit
        set_property PULLTYPE "$orig_init" $port
    }
}

proc run {} {
    make_project
    set sel_iob_sites [loc_iob]
    puts "Selected IOBs: [llength $sel_iob_sites]"

    place_design
    route_design
    write_checkpoint -force design.dcp
    write_bitstream -force design.bit

    write_iob $sel_iob_sites
}

run
