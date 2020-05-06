# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
open_checkpoint [lindex $argv 0]

# Disabling CRC just replaces the CRC register writes with Reset CRC commands.
# This seems to work via JTAG as it works in combination with PERFRAMECRC
# either when applied via Vivado (this setting) or by manually patching the
# bitstream later.
#
set_property BITSTREAM.GENERAL.CRC Disable [current_design]

# Debug bitstreams write to LOUT which is only valid on serial master/slave
# programming methods.  If those are replaced with NOPs, Reset CRC commands, or
# removed entirely, the bitstream will program (DONE light goes active) but the
# configuration doesn't start.  The JTAG status register shows BAD_PACKET_ERROR
# when this happens.  I'm guessing that the individual frame writes require the
# PERFRAMECRC approach to work at all via JTAG.
#
#set_property BITSTREAM.GENERAL.DEBUGBITSTREAM YES [current_design]

# PERFRAMECRC bitstreams can be directly loaded via JTAG.  They also use an
# undocumented bit to disable autoincrement which seems to be required if doing
# individual frame writes instead of a bulk write.  The CRC chceks after each
# frame are _required_ for this bitstream to program.
#
#set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]


write_bitstream -force [lindex $argv 1]
