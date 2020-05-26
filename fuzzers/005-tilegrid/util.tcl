# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
proc min_ysite { duts_in_column } {
    # Given a list of sites, return the one with the lowest Y coordinate

    set min_dut_y 9999999

    foreach dut $duts_in_column {
        # Ex: SLICE_X2Y50/A6LUT
        # Ex: IOB_X1Y50
        regexp ".*_X([0-9]+)Y([0-9]+)" $dut match dut_x dut_y

        if { $dut_y < $min_dut_y } {
            set selected_dut $dut
            set min_dut_y $dut_y
        }
    }
    return $selected_dut
}

proc group_dut_cols { duts ypitch } {
    # Group a list of sites into pitch sized buckets
    # Ex: IOBs occur 75 to a CMT column
    # Set pitch to 75 to get 0-74 in one bucket, 75-149 in a second, etc
    # X0Y0 {IOB_X0Y49 IOB_X0Y48 IOB_X0Y47 ... }
    # Anything with a different x is automatically in a different bucket

    # LOC one LUT (a "selected_lut") into each CLB segment configuration column (ie 50 per CMT column)
    set dut_columns ""
    foreach dut $duts {
        # Ex: SLICE_X2Y50/A6LUT
        # Ex: IOB_X1Y50
        regexp ".*_X([0-9]+)Y([0-9]+)" $dut match dut_x dut_y

        # 75 per column => 0, 75, 150, etc
        set y_column [expr ($dut_y / $ypitch) * $ypitch]
        dict append dut_columns "X${dut_x}Y${y_column}" "$dut "
    }
    return $dut_columns
}

proc loc_dut_col_bels { dut_columns cellpre cellpost } {
    # set cellpre di

    # Pick the smallest Y in each column and LOC a cell to it
    # cells must be named like $cellpre[$dut_index]
    # Return the selected sites

    set ret_bels {}
    set dut_index 0

    dict for {column duts_in_column} $dut_columns {
        set sel_bel_str [min_ysite $duts_in_column]
        set sel_bel [get_bels $sel_bel_str]
        if {"$sel_bel" == ""} {error "Bad bel $sel_bel from bel str $sel_bel_str"}
        set sel_site [get_sites -of_objects $sel_bel]
        if {"$sel_site" == ""} {error "Bad site $sel_site from bel $sel_bel"}

        set cell [get_cells $cellpre$dut_index$cellpost]
        puts "LOCing cell $cell to site $sel_site (from bel $sel_bel)"
        set_property LOC $sel_site $cell

        set dut_index [expr $dut_index + 1]
        lappend ret_bels $sel_bel
    }

    return $ret_bels
}

proc loc_dut_col_sites { dut_columns cellpre cellpost } {
    set bels [loc_dut_col_bels $dut_columns $cellpre $cellpost]
    set sites [get_sites -of_objects $bels]
    return $sites
}

proc make_io_pad_sites {} {
    # get all possible IOB pins
    foreach pad [get_package_pins -filter "IS_GENERAL_PURPOSE == 1"] {
        set site [get_sites -of_objects $pad]
        if {[llength $site] == 0} {
            continue
        }
        if [string match IOB33* [get_property SITE_TYPE $site]] {
            dict append io_pad_sites $site $pad
        }
    }
    return $io_pad_sites
}

proc make_iob_pads {} {
    set io_pad_sites [make_io_pad_sites]

    set iopad ""
    dict for {key value} $io_pad_sites {
        # Some sites have more than one pad?
        lappend iopad [lindex $value 0]
    }
    return $iopad
}

proc make_iob_sites {} {
    set io_pad_sites [make_io_pad_sites]

    set sites ""
    dict for {key value} $io_pad_sites {
        lappend sites $key
    }
    return $sites
}

proc assign_iobs_old {} {
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports di]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports do]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports stb]
}

proc assign_iobs {} {
    # Set all I/Os on the bus to valid values somewhere on the chip
    # The iob fuzzer sets these to more specific values

    # All possible IOs
    set iopad [make_iob_pads]
    # Basic pins
    # XXX: not all pads are valid, but seems to be working for now
    # Maybe better to set to XRAY_PIN_* and take out of the list?
    set_property -dict "PACKAGE_PIN [lindex $iopad 0] IOSTANDARD LVCMOS33" [get_ports clk]
    set_property -dict "PACKAGE_PIN [lindex $iopad 1] IOSTANDARD LVCMOS33" [get_ports do]
    set_property -dict "PACKAGE_PIN [lindex $iopad 2] IOSTANDARD LVCMOS33" [get_ports stb]

    # din bus
    set fixed_pins 3
    set iports [get_ports di*]
    for {set i 0} {$i < [llength $iports]} {incr i} {
        set pad [lindex $iopad [expr $i+$fixed_pins]]
        set port [lindex $iports $i]
        set_property -dict "PACKAGE_PIN $pad IOSTANDARD LVCMOS33" $port
    }
}

proc make_project {} {
    # Generate .bit only over ROI
    make_project_roi XRAY_ROI_TILEGRID XRAY_EXCLUDE_ROI_TILEGRID
}

proc make_project_roi { roi_var exclude_roi_var } {
    # 6 CMTs in our reference part
    # What is the largest?
    set n_di 16

    create_project -force -part $::env(XRAY_PART) design design

    read_verilog "$::env(FUZDIR)/top.v"
    synth_design -top top -verilog_define N_DI=$n_di

    assign_iobs

    create_pblock roi
    add_cells_to_pblock [get_pblocks roi] [get_cells roi]
    foreach roi "$::env($roi_var)" {
        puts "ROI: $roi"
        resize_pblock [get_pblocks roi] -add "$roi"
    }

    create_pblock exclude_roi
    add_cells_to_pblock [get_pblocks roi] [get_cells roi]
    foreach roi "$::env($exclude_roi_var)" {
        puts "ROI: $roi"
        resize_pblock [get_pblocks exclude_roi] -add "$roi"
    }

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
    set_param tcl.collectionResultDisplayLimit 0

    set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]
}
