# Copyright (C) 2017-2021  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
# Writes a JSON5 to filename containing timing for current design.
# This can be used with create_timing_worksheet_db.py to compare prjxray model
# with Vivado timing model outputs.
link_design -part $::env(XRAY_PART)

# one pin -> 0
set clk_pins [get_package_pins -filter "IS_CLK_CAPABLE"]

# three pins -> 1, 2, 3 on HR banks only
set banks [get_iobanks -filter "BANK_TYPE==BT_HIGH_RANGE"]

set data_pins ""
foreach bank [split $banks " "] {
    append data_pins " " [get_package_pins -filter "IS_GENERAL_PURPOSE && BANK==$bank"]
}

set fp [open $::env(TMP_FILE) w]

puts $fp "{"
    puts $fp "\t\"clk_pins\": \"$clk_pins\","
    puts $fp "\t\"data_pins\": \"$data_pins\""
puts $fp "}"
