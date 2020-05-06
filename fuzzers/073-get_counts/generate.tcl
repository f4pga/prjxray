# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
# This script dumps the count of each major object count for sanity checking.
#
# For large parts, this may take a while, hence why it is a seperate generate
# step.

create_project -force -part $::env(XRAY_PART) design design
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

set fp [open element_counts.csv w]
puts $fp "type,count"
puts $fp "tiles,[llength [get_tiles]]"
set sites [get_sites]
set num_site_pins 0
set num_site_pips 0
puts $fp "sites,[llength $sites]"
foreach site $sites {
    set num_site_pins [expr $num_site_pins + [llength [get_site_pins -of_objects $site]]]
    set num_site_pips [expr $num_site_pips + [llength [get_site_pips -of_objects $site]]]
}
puts $fp "site_pins,$num_site_pins"
puts $fp "site_pips,$num_site_pips"
puts $fp "pips,[llength [get_pips]]"
puts $fp "package_pins,[llength [get_package_pins]]"
puts $fp "nodes,[llength [get_nodes]]"
puts $fp "wires,[llength [get_wires]]"
close $fp
