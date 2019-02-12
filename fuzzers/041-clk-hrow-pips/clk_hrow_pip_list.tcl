proc print_tile_pips {tile_type filename} {
    set tile [lindex [get_tiles -filter "TYPE == $tile_type"] 0]
    puts "Dumping PIPs for tile $tile ($tile_type) to $filename."
    set fp [open $filename w]
    foreach pip [lsort [get_pips -of_objects [get_tiles $tile]]] {
        set src [get_wires -uphill -of_objects $pip]
        set dst [get_wires -downhill -of_objects $pip]
        if {[llength [get_nodes -uphill -of_objects [get_nodes -of_objects $dst]]] != 1} {
            puts $fp "$tile_type.[regsub {.*/} $dst ""].[regsub {.*/} $src ""]"
        }
    }
    close $fp
}

create_project -force -part $::env(XRAY_PART) design design
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

print_tile_pips CLK_HROW_TOP_R clk_hrow_top_r.txt
print_tile_pips CLK_HROW_BOT_R clk_hrow_bot_r.txt
