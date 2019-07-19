proc print_tile_pips {tile_type filename} {
    set fp [open $filename w]
    set pips [dict create]
    foreach tile [get_tiles -filter "TYPE == $tile_type"] {
        puts "Dumping PIPs for tile $tile ($tile_type) to $filename."
        foreach pip [lsort [get_pips -of_objects  $tile]] {
            set src [get_wires -uphill -of_objects $pip]
            set dst [get_wires -downhill -of_objects $pip]

            # Skip pips with disconnected nodes
            set src_node [get_nodes -of_objects $src]
            if { $src_node == {} } {
                continue
            }

            set dst_node [get_nodes -of_objects $dst]
            if { $dst_node == {} } {
                continue
            }

            if {[llength [get_nodes -uphill -of_objects $dst_node]] > 1} {
                set pip_string "$tile_type.[regsub {.*/} $dst ""].[regsub {.*/} $src ""]"
                if ![dict exists $pips $pip_string] {
                    puts $fp $pip_string
                    dict set pips $pip_string 1
                }
            } else {
                puts "Ignoring PIP: $pip"
            }
        }
    }
    close $fp
}

create_project -force -part $::env(XRAY_PART) design design
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

print_tile_pips HCLK_IOI3 hclk_ioi3.txt
