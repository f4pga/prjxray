# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
source "$::env(XRAY_DIR)/utils/utils.tcl"

proc make_manual_routes {filename} {
    puts "MANROUTE: Loading routes from $filename"

    set fp [open $filename r]
    foreach line [split [read $fp] "\n"] {
        if {$line eq ""} {
            continue
        }

        puts "MANROUTE: Line: $line"

        # Parse the line
        set fields [split $line " "]
        set net_name [lindex $fields 0]
        set wire_name [lindex $fields 1]

        # Check if that net exist
        if {[get_nets $net_name] eq ""} {
            puts "MANROUTE: net $net_name does not exist"
            continue
        }

        # Make the route
        set status [route_via $net_name [list $wire_name] 0]

        # Failure, skip manual routing of this net
        if { $status != 1 } {
            puts "MANROUTE: Manual routing failed!"
            set net [get_nets $net_name]
            set_property -quiet FIXED_ROUTE "" $net
            set_property IS_ROUTE_FIXED 0 $net
            continue
        }

        puts "MANROUTE: Success!"
    }
}

create_project -force -part $::env(XRAY_PART) design design
read_verilog top.v
synth_design -top top

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

create_clock -period 10.00 [get_ports clkin1*]
create_clock -period 10.00 [get_ports clkin2*]

# Disable MMCM frequency etc sanity checks
set_property IS_ENABLED 0 [get_drc_checks {PDRC-29}]
set_property IS_ENABLED 0 [get_drc_checks {PDRC-30}]
set_property IS_ENABLED 0 [get_drc_checks {AVAL-50}]
set_property IS_ENABLED 0 [get_drc_checks {AVAL-53}]
set_property IS_ENABLED 0 [get_drc_checks {REQP-126}]
# PLL
set_property IS_ENABLED 0 [get_drc_checks {PDRC-43}]
set_property IS_ENABLED 0 [get_drc_checks {REQP-161}]
set_property IS_ENABLED 0 [get_drc_checks {AVAL-78}]

set_property IS_ENABLED 0 [get_drc_checks {UCIO-1}]
set_property IS_ENABLED 0 [get_drc_checks {NSTD-1}]

place_design
write_checkpoint -force design_placed.dcp

make_manual_routes routes.txt
write_checkpoint -force design_pre_route.dcp

route_design -directive Quick -preserve

set unrouted_nets [get_nets -filter {ROUTE_STATUS!="ROUTED"}]
if {[llength $unrouted_nets] ne 0} {
    puts "MANROUTE: Got unrouted nets: $unrouted_nets"
    puts "MANROUTE: Ripping up and starting again with no fixed routes"

    route_design -unroute

    set fixed_nets [get_nets -filter {IS_ROUTE_FIXED==1}]
    if {[llength $fixed_nets] ne 0} {
        set_property FIXED_ROUTE "" $fixed_nets
        set_property IS_ROUTE_FIXED 0 $fixed_nets
    }

    route_design -directive Quick
}

write_checkpoint -force design.dcp
write_bitstream -force design.bit

set fp [open params.json "w"]
puts $fp "\["
foreach cell [get_cells -hierarchical -filter {REF_NAME == PLLE2_ADV}] {
    puts $fp " {"
        puts $fp "   \"tile\": \"[get_tiles -of [get_sites -of $cell]]\","
        puts $fp "   \"site\": \"[get_sites -of $cell]\","
        puts $fp "   \"params\": {"
            foreach prop [list_property $cell] {
                puts $fp "    \"$prop\": \"[get_property $prop $cell]\","
            }
        puts $fp "   }"
    puts $fp " },"

}
puts $fp "\]"
close $fp
