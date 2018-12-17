source "$::env(XRAY_DIR)/utils/utils.tcl"

create_project -force -part $::env(XRAY_PART) design design

read_verilog $::env(FUZDIR)/top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports i]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports o]

create_pblock roi
resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
set_param tcl.collectionResultDisplayLimit 0

place_design
route_design

# write_checkpoint -force design.dcp

set fp [open "../../todo.txt" r]
set todo_lines {}
for {gets $fp line} {$line != ""} {gets $fp line} {
    lappend todo_lines [split $line .]
}
close $fp

set int_l_tiles [randsample_list [llength $todo_lines] [filter [pblock_tiles roi] {TYPE == INT_L}]]
set int_r_tiles [randsample_list [llength $todo_lines] [filter [pblock_tiles roi] {TYPE == INT_R}]]

for {set idx 0} {$idx < [llength $todo_lines]} {incr idx} {
    set line [lindex $todo_lines $idx]
    puts "== $idx: $line"

    set tile_type [lindex $line 0]
    set dst_wire [lindex $line 1]
    set src_wire [lindex $line 2]

    if {$tile_type == "INT_L"} {set tile [lindex $int_l_tiles $idx]; set other_tile [lindex $int_r_tiles $idx]}
    if {$tile_type == "INT_R"} {set tile [lindex $int_r_tiles $idx]; set other_tile [lindex $int_l_tiles $idx]}

    puts "PIP Tile: $tile"

    set driver_site [get_sites -of_objects [get_site_pins -of_objects [get_nodes -downhill \
            -of_objects [get_nodes -of_objects [get_wires $other_tile/CLK*0]]]]]

    puts "LUT Tile (Site): $other_tile ($driver_site)"

    set mylut [create_cell -reference LUT1 mylut_$idx]
    set_property -dict "LOC $driver_site BEL A6LUT" $mylut

    set mynet [create_net mynet_$idx]
    connect_net -net $mynet -objects "$mylut/I0 $mylut/O"
    route_via $mynet "$tile/$src_wire $tile/$dst_wire"
}

proc write_txtdata {filename} {
    puts "Writing $filename."
    set fp [open $filename w]
    set all_pips [lsort -unique [get_pips -of_objects [get_nets -hierarchical]]]
    if {$all_pips != {}} {
        puts "Dumping pips."
        foreach tile [get_tiles [regsub -all {CLBL[LM]} [get_tiles -of_objects [get_sites -of_objects [get_pblocks roi]]] INT]] {
            foreach pip [filter $all_pips "TILE == $tile"] {
                set src_wire [get_wires -uphill -of_objects $pip]
                set dst_wire [get_wires -downhill -of_objects $pip]
                set num_pips [llength [get_nodes -uphill -of_objects [get_nodes -of_objects $dst_wire]]]
                set dir_prop [get_property IS_DIRECTIONAL $pip]
                puts $fp "$tile $pip $src_wire $dst_wire $num_pips $dir_prop"
            }
        }
    }
    close $fp
}

route_design

# Ex: ERROR: [DRC RTSTAT-5] Partial antennas: 1 net(s) have a partial antenna. The problem bus(es) and/or net(s) are mynet_2.
# set_property IS_ENABLED 0 [get_drc_checks {RTSTAT-5}]

write_checkpoint -force design.dcp
write_bitstream -force design.bit
write_txtdata design.txt
