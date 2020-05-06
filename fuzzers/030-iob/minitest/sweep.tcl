# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
# Sweep all values of $prop on given I/O $port
# Write out bitstream for all legal values

set vals [list_property_value $prop $port]
foreach {val} $vals {
    puts $val
    # Not all listable properties are settable
    # Its easiest to try setting and see if it sticks
    set_property -quiet $prop $val $port
    set got [get_property $prop $port]
    if {"$got" != "$val"} {
        puts "  Skipping: wanted $val, got $got"
        continue
    }
    if {[catch {write_bitstream -force design_$val.bit} issue]} {
        puts "WARNING failed to write: $issue"
        continue
    }
    # Only write checkpoints for acceptable bitstreams
    write_checkpoint -force design_$val.dcp
}
