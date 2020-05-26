# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

foreach tile [get_tiles] {
    foreach prop [list_property $tile] {
        puts "--tiledata-- TILEPROP $tile $prop [get_property $prop $tile]"
    }
    foreach site [get_sites -quiet -of_objects $tile] {
        puts "--tiledata-- TILESITE $tile $site"
    }
}

foreach site [get_sites] {
    foreach prop [list_property $site] {
        puts "--tiledata-- SITEPROP $site $prop [get_property $prop $site]"
    }
}
