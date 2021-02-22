# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
create_project -force -part $::env(XRAY_PART) design design

read_verilog $::env(FUZDIR)/top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports a]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports y]

create_pblock roi
resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
set_param tcl.collectionResultDisplayLimit 0

place_design
route_design

write_checkpoint -force design.dcp
# write_bitstream -force design.bit

proc write_clb_ppips_db {filename tile} {
    set fp [open $filename "w"]
    set tile [get_tiles $tile]
    set tile_type [get_property TILE_TYPE $tile]

    foreach pip [get_pips -of_objects $tile] {
        set dst_wire [get_wires -downhill -of_objects $pip]
        if {[get_property IS_PSEUDO $pip]} {
            set src_wire [get_wires -uphill -of_objects $pip]
            puts $fp "${tile_type}.[regsub {.*/} $dst_wire ""].[regsub {.*/} $src_wire ""] hint"
        } elseif {[get_pips -uphill -of_objects [get_nodes -of_objects $dst_wire]] == $pip} {
            set src_wire [get_wires -uphill -of_objects $pip]
            puts $fp "${tile_type}.[regsub {.*/} $dst_wire ""].[regsub {.*/} $src_wire ""] always"
        }
    }

    close $fp
}

proc write_int_ppips_db {filename tile} {
    set fp [open $filename "w"]
    set tile [get_tiles $tile]
    set tile_type [get_property TILE_TYPE $tile]

    foreach pip [get_pips -of_objects [get_wires $tile/VCC_WIRE]] {
        set wire [regsub {.*/} [get_wires -downhill -of_objects $pip] ""]
        puts $fp "${tile_type}.${wire}.VCC_WIRE default"
    }

    foreach pip [get_pips -of_objects $tile] {
        set dst_wire [get_wires -downhill -of_objects $pip]
        if {[get_pips -uphill -of_objects [get_nodes -of_objects $dst_wire]] == $pip} {
            set src_wire [get_wires -uphill -of_objects $pip]
            puts $fp "${tile_type}.[regsub {.*/} $dst_wire ""].[regsub {.*/} $src_wire ""] always"
        }
    }

    close $fp
}

proc write_bram_ppips_db {filename tile} {
    set fp [open $filename "w"]
    set tile [get_tiles $tile]
    set tile_type [get_property TILE_TYPE $tile]

    foreach pip [get_pips -of_objects $tile] {
        set dst_wire [get_wires -downhill -of_objects $pip]
        if {[get_pips -uphill -of_objects [get_nodes -of_objects $dst_wire]] == $pip} {
            set src_wire [get_wires -uphill -of_objects $pip]
            puts $fp "${tile_type}.[regsub {.*/} $dst_wire ""].[regsub {.*/} $src_wire ""] always"
        } elseif [string match "*LOGIC_OUTS*" $dst_wire] {
            # LOGIC_OUTS pips appear to be always, even thought multiple inputs to
            # the pip junction.  Best guess is that the underlying hardware is
            # actually just one wire, and there is no actual junction.
            foreach src_wire [get_wires -uphill -of_objects $pip] {
                puts $fp "${tile_type}.[regsub {.*/} $dst_wire ""].[regsub {.*/} $src_wire ""] always"
            }
        }
    }

    close $fp
}

proc write_hclk_ppips_db {filename tile} {
    set fp [open $filename "w"]
    set tile [get_tiles $tile]
    set tile_type [get_property TILE_TYPE $tile]

    foreach pip [get_pips -of_objects $tile] {
        set dst_wire [get_wires -downhill -of_objects $pip]
        if [string match "*HCLK_IOI_CK_IGCLK*" $dst_wire] {
            continue
        } elseif {[get_pips -uphill -of_objects [get_nodes -of_objects $dst_wire]] == $pip} {
            set src_wire [get_wires -uphill -of_objects $pip]
            puts $fp "${tile_type}.[regsub {.*/} $dst_wire ""].[regsub {.*/} $src_wire ""] always"
        }
    }

    close $fp
}

proc write_ioi_ppips_db {filename tile} {
    set fp [open $filename "w"]
    set tile [get_tiles $tile]
    set tile_type [get_property TILE_TYPE $tile]

    foreach pip [get_pips -of_objects $tile] {
        set dst_wire [get_wires -downhill -of_objects $pip]
        if [string match "*DATAOUT*" $dst_wire] {
            continue
        } elseif {[get_pips -uphill -of_objects [get_nodes -of_objects $dst_wire]] == $pip} {
            set src_wire [get_wires -uphill -of_objects $pip]
            puts $fp "${tile_type}.[regsub {.*/} $dst_wire ""].[regsub {.*/} $src_wire ""] always"
        }
    }

    close $fp
}

proc write_pss_ppips_db {filename tile} {
    if {[llength $tile] != 0} {
        set fp [open $filename "w"]
        set tile [get_tiles $tile]
        set tile_type [get_property TILE_TYPE $tile]

        # Skip bi-directional PIPs as they represent hard-wired PS7 connections
        # and are not routable.
        foreach pip [get_pips -of_objects $tile -filter "IS_DIRECTIONAL == 1"] {
            set dst_wire [get_wires -downhill -of_objects $pip]
            if {[get_pips -uphill -of_objects [get_nodes -of_objects $dst_wire]] == $pip} {
                set src_wire [get_wires -uphill -of_objects $pip]
                puts $fp "${tile_type}.[regsub {.*/} $dst_wire ""].[regsub {.*/} $src_wire ""] always"
            }
        }

        close $fp
    }
}

proc write_gtp_channel_ppips_db {filename tile tile_suffix} {
    set fp [open $filename "w"]
    set tile [get_tiles $tile]
    set tile_type [get_property TILE_TYPE $tile]

    foreach pip [get_pips -of_objects $tile] {
        set dst_wire [get_wires -downhill -of_objects $pip]
        if {[get_pips -uphill -of_objects [get_nodes -of_objects $dst_wire]] == $pip} {
            set src_wire [get_wires -uphill -of_objects $pip]

            if {![regexp "IMUX" $src_wire] && ![regexp "GTPE2_CTRL" $src_wire] && ![regexp "GTPE2_CLK" $src_wire]} {
                continue
            }

            puts $fp "${tile_type}${tile_suffix}.[regsub {.*/} $dst_wire ""].[regsub {.*/} $src_wire ""] always"
        }
    }

    close $fp
}

proc write_gtp_int_interface_ppips_db {filename tile} {
    set fp [open $filename "w"]
    set tile [get_tiles $tile]
    set tile_type [get_property TILE_TYPE $tile]

    foreach pip [get_pips -of_objects $tile] {
        set dst_wire [get_wires -downhill -of_objects $pip]
        set src_wire [get_wires -uphill -of_objects $pip]

        if {![regexp "IMUX_OUT" $dst_wire]} {
            continue
        }

        if {[regexp "DELAY" $src_wire]} {
            continue
        }

        puts $fp "${tile_type}.[regsub {.*/} $dst_wire ""].[regsub {.*/} $src_wire ""] always"
    }

    close $fp
}

foreach tile_type {CLBLM_L CLBLM_R CLBLL_L CLBLL_R} {
    set tiles [get_tiles -filter "TILE_TYPE == $tile_type"]
    if {[llength $tiles] != 0} {
        set tile [lindex $tiles 0]
        write_clb_ppips_db "ppips_[string tolower $tile_type].db" $tile
    }
}

foreach tile_type {INT_L INT_R  BRAM_INT_INTERFACE_L BRAM_INT_INTERFACE_R \
            CLK_HROW_TOP_R CLK_HROW_BOT_R CLK_BUFG_TOP_R CLK_BUFG_BOT_R \
            IO_INT_INTERFACE_R IO_INT_INTERFACE_L \
            BRKH_INT HCLK_L HCLK_R HCLK_CMT \
            CMT_TOP_L_UPPER_T CMT_TOP_L_UPPER_B \
            CMT_TOP_L_LOWER_T CMT_TOP_L_LOWER_B \
            CMT_TOP_R_UPPER_T CMT_TOP_R_UPPER_B \
            CMT_TOP_R_LOWER_T CMT_TOP_R_LOWER_B \
            INT_INTERFACE_L INT_INTERFACE_R} {
    set tiles [get_tiles -filter "TILE_TYPE == $tile_type"]
    if {[llength $tiles] != 0} {
        set tile [lindex $tiles 0]
        write_int_ppips_db "ppips_[string tolower $tile_type].db" $tile
    }
}

foreach tile_type {HCLK_IOI3} {
    set tiles [get_tiles -filter "TILE_TYPE == $tile_type"]
    if {[llength $tiles] != 0} {
        set tile [lindex $tiles 0]
        write_hclk_ppips_db "ppips_[string tolower $tile_type].db" $tile
    }
}

foreach tile_type {RIOI3 LIOI3 LIOI3_TBYTETERM RIOI3_TBYTETERM \
            LIOI3_TBYTESRC RIOI3_TBYTESRC LIOI3_SING RIOI3_SING} {
    set tiles [get_tiles -filter "TILE_TYPE == $tile_type"]
    if {[llength $tiles] != 0} {
        set tile [lindex $tiles 0]
        write_ioi_ppips_db "ppips_[string tolower $tile_type].db" $tile
    }
}

foreach tile_type {BRAM_L BRAM_R} {
    set tiles [get_tiles -filter "TILE_TYPE == $tile_type"]
    if {[llength $tiles] != 0} {
        set tile [lindex $tiles 0]
        write_bram_ppips_db "ppips_[string tolower $tile_type].db" $tile
    }
}

foreach tile_type {PSS0 PSS1 PSS2 PSS3 PSS4 INT_INTERFACE_PSS_L} {
    set tiles [get_tiles -filter "TILE_TYPE == $tile_type"]
    if {[llength $tiles] != 0} {
        set tile [lindex $tiles 0]
        write_pss_ppips_db "ppips_[string tolower $tile_type].db" $tile
    }
}

foreach tile_type {GTP_CHANNEL_0 GTP_CHANNEL_1 GTP_CHANNEL_2 GTP_CHANNEL_3 GTP_COMMON} {
    set tiles [get_tiles -filter "TILE_TYPE == $tile_type"]
    if {[llength $tiles] != 0} {
        set tile [lindex $tiles 0]
        write_gtp_channel_ppips_db "ppips_[string tolower $tile_type].db" $tile ""
        write_gtp_channel_ppips_db "ppips_[string tolower $tile_type]_mid_left.db" $tile "_MID_LEFT"
        write_gtp_channel_ppips_db "ppips_[string tolower $tile_type]_mid_right.db" $tile "_MID_RIGHT"
    }
}

foreach tile_type {GTP_INT_INTERFACE} {
    set tiles [get_tiles -filter "TILE_TYPE == $tile_type"]
    if {[llength $tiles] != 0} {
        set tile [lindex $tiles 0]
        write_gtp_int_interface_ppips_db "ppips_[string tolower $tile_type].db" $tile
    }
}
