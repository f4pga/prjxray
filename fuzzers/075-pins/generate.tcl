create_project -force -part $::env(XRAY_PART) design design
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

set fp [open $::env(XRAY_PART)_package_pins.csv w]
puts $fp "pin,site,tile"
foreach pin [get_package_pins] {
    set site [get_sites -quiet -of_object $pin]
    if { $site == "" } {
        continue
    }

    set tile [get_tiles -of_object $site]

    puts $fp "$pin,$site,$tile"
}
