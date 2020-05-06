# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set sites [get_sites -filter {(SITE_TYPE == "SLICEL" || SITE_TYPE == "SLICEM") && (NAME =~ "*Y0" || NAME =~ "*Y50" || NAME =~ "*Y?00" || NAME =~ "*Y?50")}]

foreach site $sites {
    puts ""; puts ""; puts ""; puts ""; puts ""; puts ""
    puts "=========================== $site ==========================="

    set_property LOC $site [get_cells lut]
    route_design

    set_property INIT 64'h8000000000000000 [get_cells lut]
    write_bitstream -force logicframes_${site}_0.bit

    set_property INIT 64'h8000000000000001 [get_cells lut]
    write_bitstream -force logicframes_${site}_1.bit
}
