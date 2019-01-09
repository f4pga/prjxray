source "$::env(XRAY_DIR)/utils/utils.tcl"

create_project -force -part $::env(XRAY_PART) design design

read_verilog $::env(FUZDIR)/top.v
read_verilog $::env(FUZDIR)/picorv32.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports din]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports dout]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports stb]

create_pblock roi
resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]
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

set int_l_tiles [filter [pblock_tiles roi] {TYPE == INT_L}]]
set int_r_tiles [filter [pblock_tiles roi] {TYPE == INT_R}]]

for {set idx 0} {$idx < [llength $todo_lines]} {incr idx} {
    set line [lindex $todo_lines $idx]

    set tile_type [lindex $line 0]
    set dst_wire [lindex $line 1]
    set src_wire [lindex $line 2]

    if {$tile_type == "INT_L"} {set tile [lindex $int_l_tiles $idx]}
    if {$tile_type == "INT_R"} {set tile [lindex $int_r_tiles $idx]}

    set clb_dst_wire [get_wires -filter {TILE_NAME =~ CLB*} -of_objects [get_nodes -of_objects [get_wire $tile/$dst_wire]]]
    set clb_src_wire [get_wires -filter {TILE_NAME =~ CLB*} -of_objects [get_nodes -of_objects [get_wire $tile/$src_wire]]]

    set clb_dst_pin [get_site_pins -of_objects [get_nodes -downhill -of_objects [get_pips -of_objects $clb_dst_wire]]]
    set clb_src_pin [get_site_pins -of_objects [get_nodes -uphill -of_objects [get_pips -of_objects $clb_src_wire]]]

    set src_prefix [regsub {(.*/.).*} ${clb_src_pin} {\1}]
    set dst_prefix [regsub {(.*/.).*} ${clb_dst_pin} {\1}]

    set slice [get_sites -of_objects $clb_dst_pin]
    set src_slice [get_sites -of_objects $clb_src_pin]
    set lut [regsub {.*/} $src_prefix {}]6LUT
    set dff [regsub {.*/} $src_prefix {}]FF

    set mynet [create_net mynet_$idx]
    set mylut [create_cell -reference LUT1 mylut_$idx]
    set lutin [regsub {.*(.)} $clb_dst_pin {A\1}]
    set_property -dict "LOC $slice BEL $lut LOCK_PINS I0:$lutin" $mylut

    # some source wires may be FF outputs, in such cases
    # we need to place and route an FF

    set src_type [regsub {.*/*(.$)} $clb_src_pin {\1}]
    if { $src_type == "Q" } {
        set mydff [create_cell -reference FDCE mydff_$idx]
        set_property -dict "LOC $src_slice BEL $dff" $mydff
        connect_net -net $mynet -objects "$mylut/I0 $mydff/Q"
    } else {
        connect_net -net $mynet -objects "$mylut/I0 $mylut/O"
    }

    set route_list "$tile/$src_wire $tile/$dst_wire"
    puts "route_via $mynet $route_list"
    set rc [route_via $mynet $route_list 0]
    if {$rc != 0} {
        puts "SUCCESS"
    } else {
        puts "Manual routing failed"
        # TODO: We should probably fail here
    }
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
write_checkpoint -force design.dcp
write_bitstream -force design.bit
write_txtdata design.txt
