create_project -force -part $::env(XRAY_PART) design design
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1
set fp [open "iobanks.txt" "w"]
foreach iobank [get_iobanks] {
    foreach site [get_sites -of $iobank] {
        puts $fp "$site,$iobank"
    }
}
close $fp

set fp [open "cmt_regions.csv" "w"]
foreach site_type { IOB33M IOB33S IDELAYCTRL} {
    foreach site [get_sites -filter "SITE_TYPE == $site_type"] {
        set tile [get_tiles -of $site]
        puts $fp "$site,$tile,[get_property CLOCK_REGION $site]"
    }
}
close $fp
