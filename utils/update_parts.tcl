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
set parts [get_parts -filter "FAMILY == $::env(FILTER)"]
foreach part $parts {
    puts "$part,[get_property DEVICE $part],[get_property PACKAGE $part],[get_property SPEED $part]"
}
