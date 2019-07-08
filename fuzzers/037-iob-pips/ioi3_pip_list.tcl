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

            set dst_node [get_nodes -of_objects $src]
            if { $dst_node == {} } {
                continue
            }

            if {[llength [get_nodes -uphill -of_objects [get_nodes -of_objects $dst]]] != 1} {
                set pip_string "$tile_type.[regsub {.*/} $dst ""].[regsub {.*/} $src ""]"
                if ![dict exists $pips $pip_string] {
                    puts $fp $pip_string
                    dict set pips $pip_string 1
                }
            }
        }
    }
    close $fp
}

create_project -force -part $::env(XRAY_PART) design design
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

# Cleaning ioi3.txt pip file
set fp [open ioi3.txt w]
close $fp

print_tile_pips LIOI3 ioi3_l.txt
print_tile_pips RIOI3 ioi3_r.txt
