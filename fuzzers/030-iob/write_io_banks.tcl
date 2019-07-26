create_project -force -part $::env(XRAY_PART) design design
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1
set fp [open "iobanks.txt" "w"]
foreach iobank [get_iobanks] {
    puts $fp $iobank
}
close $fp
