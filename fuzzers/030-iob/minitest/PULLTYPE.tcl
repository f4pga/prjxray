# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
source "$::env(SRC_DIR)/template.tcl"

set port [get_ports di]

set_property PULLTYPE "" $port
write_checkpoint -force design_NONE.dcp
write_bitstream -force design_NONE.bit

set vals "KEEPER PULLUP PULLDOWN"
foreach {val} $vals {
    set_property PULLTYPE $val $port
    write_checkpoint -force design_$val.dcp
    write_bitstream -force design_$val.bit
}
