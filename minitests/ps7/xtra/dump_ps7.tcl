create_project -force -in_memory -name design -part xc7z020clg400-1
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

set fp [open ps7.csv w]
puts $fp "name,is_input,is_output"

set pins [get_bel_pins -of_objects [get_bels -of_objects [get_sites PS7* -of_objects [get_tiles PSS*]]]]
foreach pin $pins {

    set pin_name [lindex [split $pin "/"] 2]
    set is_input [get_property IS_INPUT $pin]
    set is_output [get_property IS_OUTPUT $pin]

    puts $fp "$pin_name,$is_input,$is_output"
}

close $fp
