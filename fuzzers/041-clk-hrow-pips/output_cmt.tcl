create_project -force -part $::env(XRAY_PART) design design
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

set fp [open "cmt_regions.csv" "w"]
foreach site_type {MMCME2_ADV PLLE2_ADV BUFHCE BUFR} {
    foreach site [get_sites -filter "SITE_TYPE == $site_type"] {
        puts $fp "$site,[get_property CLOCK_REGION $site]"
    }
}
close $fp
