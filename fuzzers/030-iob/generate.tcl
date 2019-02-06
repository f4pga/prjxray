source "$::env(XRAY_DIR)/utils/utils.tcl"

proc make_io_pin_sites {} {
    # get all possible IOB pins
    foreach pad [get_package_pins -filter "IS_GENERAL_PURPOSE == 1"] {
        set site [get_sites -of_objects $pad]
        if {[llength $site] == 0} {
            continue
        }
        if [string match IOB33* [get_property SITE_TYPE $site]] {
            dict append io_pin_sites $site $pad
        }
    }
    return $io_pin_sites
}

proc load_pin_lines {} {
    # IOB_X0Y103 clk input
    # IOB_X0Y129 do[0] output

    set fp [open "params.csv" r]
    set pin_lines {}
    for {gets $fp line} {$line != ""} {gets $fp line} {
        lappend pin_lines [split $line ","]
    }
    close $fp
    return $pin_lines
}

proc loc_pins {} {
    set pin_lines [load_pin_lines]
    set io_pin_sites [make_io_pin_sites]

    set fp [open "design.csv" w]
    puts $fp "port,site,tile,pin,iostandard,slew,drive,pulltype"

    puts "Looping"
    for {set idx 0} {$idx < [llength $pin_lines]} {incr idx} {
        set line [lindex $pin_lines $idx]
        puts "$line"

        set site_str [lindex $line 0]
        set pin_str [lindex $line 1]
        set io [lindex $line 2]
        set cell_str [lindex $line 3]

        # Have: site
        # Want: pin for site
        set site [get_sites $site_str]
        set pad_bel [get_bels -of_objects $site -filter {TYPE =~ PAD && NAME =~ IOB_*}]
        # set port [get_ports -of_objects $site]
        set port [get_ports $pin_str]
        set tile [get_tiles -of_objects $site]
        set pin [dict get $io_pin_sites $site]

        set iostandard_val "LVCMOS25"
        set_property -dict "PACKAGE_PIN $pin IOSTANDARD $iostandard_val" $port

        set pulltype "NONE PULLUP PULLDOWN KEEPER"
        set pulltype_val [randsample_list 1 $pulltype]
        if { $pulltype_val == "NONE" } {
            set pulltype_val ""
        }
        set_property PULLTYPE $pulltype_val $port

        if {$io == "input"} continue

        set drive "4 8 12 16"
        set drive_val [lindex $drive [expr {$idx % 4}]]
        set_property DRIVE $drive_val $port

        set slew "SLOW FAST"
        set slew_val [lindex $slew [expr {($idx + ($idx / 4)) % 2}]]
        set_property SLEW $slew_val $port

        puts $fp "$port,$site,$tile,$pin,$iostandard_val,$slew_val,$drive_val,$pulltype_val"
    }
    close $fp
}

proc run {} {
    create_project -force -part $::env(XRAY_PART) design design
    read_verilog top.v
    synth_design -top top

    # Mostly doesn't matter since IOB are special, but add anyway
    create_pblock roi
    add_cells_to_pblock [get_pblocks roi] [get_cells roi]
    resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

    loc_pins

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
    set_param tcl.collectionResultDisplayLimit 0

    place_design
    route_design

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
}

run
