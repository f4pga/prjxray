# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
# WARNING: this is somewhat paramaterized, but is only tested on A50T/A35T with the traditional ROI
# Your ROI should at least have a SLICEL on the left

# Number of package inputs going to ROI
set DIN_N 8
if { [info exists ::env(DIN_N) ] } {
    set DIN_N "$::env(DIN_N)"
}
# Number of ROI outputs going to package
set DOUT_N 8
if { [info exists ::env(DOUT_N) ] } {
    set DOUT_N "$::env(DOUT_N)"
}
# How many rows between pins
# Reduces routing pressure
set PITCH 1
if { [info exists ::env(PITCH) ] } {
    set PITCH "$::env(PITCH)"
}

if { [info exists ::env(XRAY_ROI_HCLK)] } {
    set XRAY_ROI_HCLK "$::env(XRAY_ROI_HCLK)"
} else {
    puts "WARNING: No HCLK has been set"
}

# Setting all the PIPs for DIN and DOUT
if { [info exists ::env(XRAY_ROI_DIN_LPIP)] } {
    set DIN_LPIP "$::env(XRAY_ROI_DIN_LPIP)"
} else { puts "Warning: No left pip for DIN has been set"  }

if { [info exists ::env(XRAY_ROI_DIN_RPIP)] } {
    set DIN_RPIP "$::env(XRAY_ROI_DIN_RPIP)"
} else { puts "Warning: No right pip for DIN has been set"  }

if { [info exists ::env(XRAY_ROI_DOUT_LPIP)] } {
    set DOUT_LPIP "$::env(XRAY_ROI_DOUT_LPIP)"
} else { puts "Warning: No left pip for DOUT has been set"  }

if { [info exists ::env(XRAY_ROI_DOUT_RPIP)] } {
    set DOUT_RPIP "$::env(XRAY_ROI_DOUT_RPIP)"
} else { puts "Warning: No right pip for DOUT has been set"  }

# Setting all INT_L/R tiles for DIN and DOUT X values
if { [info exists ::env(XRAY_ROI_DIN_INT_L_X)] } {
    set DIN_INT_L_X "$::env(XRAY_ROI_DIN_INT_L_X)"
} else { puts "Warning: No INT_L for DIN has been set"  }

if { [info exists ::env(XRAY_ROI_DIN_INT_R_X)] } {
    set DIN_INT_R_X "$::env(XRAY_ROI_DIN_INT_R_X)"
} else { puts "Warning: No INT_R for DIN has been set"  }

if { [info exists ::env(XRAY_ROI_DOUT_INT_L_X)] } {
    set DOUT_INT_L_X "$::env(XRAY_ROI_DOUT_INT_L_X)"
} else { puts "Warning: No INT_L for DOUT has been set"  }

if { [info exists ::env(XRAY_ROI_DOUT_INT_R_X)] } {
    set DOUT_INT_R_X "$::env(XRAY_ROI_DOUT_INT_R_X)"
} else { puts "Warning: No INT_R for DOUT has been set"  }

# X12 in the ROI, X10 just to the left
# Start at bottom left of ROI and work up
# (IOs are to left)
# SLICE_X12Y100:SLICE_X27Y149
# set X_BASE 12
set XRAY_ROI_X0 [lindex [split [lindex [split "$::env(XRAY_ROI)" Y] 0] X] 1]
set XRAY_ROI_X1 [lindex [split [lindex [split "$::env(XRAY_ROI)" X] 2] Y] 0]
set XRAY_ROI_Y0 [lindex [split [lindex [split "$::env(XRAY_ROI)" Y] 1] :] 0]
set XRAY_ROI_Y1 [lindex [split "$::env(XRAY_ROI)" Y] 2]

set X_BASE $XRAY_ROI_X0
set Y_BASE $XRAY_ROI_Y0

set Y_CLK_BASE $Y_BASE
# Clock lut in middle
set Y_DIN_BASE [expr "$Y_CLK_BASE + $PITCH"]
# Sequential
# set Y_DOUT_BASE [expr "$Y_DIN_BASE + $DIN_N"]
# At top. This relieves routing pressure by spreading things out
# Note: can actually go up one more if we want
set Y_DOUT_BASE [expr "$XRAY_ROI_Y1 - $DOUT_N * $PITCH"]

# Y_OFFSET: offset amount to shift the components on the y column to avoid hard blocks
set Y_OFFSET 24

set part "$::env(XRAY_PART)"
set pincfg ""
if { [info exists ::env(XRAY_PINCFG) ] } {
    set pincfg "$::env(XRAY_PINCFG)"
}
set roiv "../roi_base.v"
if { [info exists ::env(XRAY_ROIV) ] } {
    set roiv "$::env(XRAY_ROIV)"
}
set roiv_trim [string map {.v v} $roiv]

puts "Environment"
puts "  XRAY_ROI: $::env(XRAY_ROI)"
puts "  X_BASE: $X_BASE"
puts "  Y_DIN_BASE: $Y_DIN_BASE"
puts "  Y_CLK_BASE: $Y_CLK_BASE"
puts "  Y_DOUT_BASE: $Y_DOUT_BASE"

source ../../../utils/utils.tcl

create_project -force -part $::env(XRAY_PART) design design
read_verilog ../top.v
read_verilog $roiv
set fixed_xdc ""
if { [info exists ::env(XRAY_FIXED_XDC) ] } {
    set fixed_xdc "$::env(XRAY_FIXED_XDC)"
}

# added flatten_hierarchy
# dout_shr was getting folded into the pblock
# synth_design -top top -flatten_hierarchy none -no_lc -keep_equivalent_registers -resource_sharing off
synth_design -top top -flatten_hierarchy none -verilog_define DIN_N=$DIN_N -verilog_define DOUT_N=$DOUT_N

if {$fixed_xdc ne ""} {
    read_xdc $fixed_xdc
}

# Map of top level net names to IOB pin names
array set net2pin [list]

# Create pin assignments based on what we are targetting
# A50T I/O Bank 16 sequential layout
if {$part eq "xc7a50tfgg484-1"} {
    # Partial list, expand as needed
    set bank_16 "F21 G22 G21 D21 E21 D22 E22 A21 B21 B22 C22 C20 D20 F20 F19 A19 A18"
    set banki 0

    # CLK
    set pin [lindex $bank_16 $banki]
    incr banki
    set net2pin(clk) $pin

    # DIN
    for {set i 0} {$i < $DIN_N} {incr i} {
        set pin [lindex $bank_16 $banki]
        incr banki
        set net2pin(din[$i]) $pin
    }

    # DOUT
    for {set i 0} {$i < $DOUT_N} {incr i} {
        set pin [lindex $bank_16 $banki]
        incr banki
        set net2pin(dout[$i]) $pin
    }
} elseif {$part eq "xc7a35tcsg324-1"} {
    if {$pincfg eq "ARTY-A7-SWBUT"} {
        # Arty A7 switch, button, and LED
        # https://reference.digilentinc.com/reference/programmable-logic/arty/reference-manual?redirect=1
        # 4 switches then 4 buttons
        set sw_but "A8 C11 C10 A10  C9 B9 B8 D9"
        # 4 LEDs then 4 RGB LEDs (green only)
        set leds "H5 J5 T9 T10  F6 J4 J2 H6"

        # 100 MHz CLK onboard
        set pin "E3"
        set net2pin(clk) $pin

        # DIN
        for {set i 0} {$i < $DIN_N} {incr i} {
            set pin [lindex $sw_but $i]
            set net2pin(din[$i]) $pin
        }

        # DOUT
        for {set i 0} {$i < $DOUT_N} {incr i} {
            set pin [lindex $leds $i]
            set net2pin(dout[$i]) $pin
        }

    } elseif {$pincfg eq "ARTY-A7-PMOD"} {
        # Arty A7 pmod
        # Disabled per above
        # https://reference.digilentinc.com/reference/programmable-logic/arty/reference-manual?redirect=1
        set pmod_ja "G13 B11 A11 D12  D13 B18 A18 K16"
        set pmod_jb "E15 E16 D15 C15  J17 J18 K15 J15"
        set pmod_jc "U12 V12 V10 V11  U14 V14 T13 U13"

        # CLK on Pmod JA
        set pin [lindex $pmod_ja 0]
        set net2pin(clk) $pin

        # DIN on Pmod JB
        for {set i 0} {$i < $DIN_N} {incr i} {
            set pin [lindex $pmod_jb $i]
            set net2pin(din[$i]) $pin
        }

        # DOUT on Pmod JC
        for {set i 0} {$i < $DOUT_N} {incr i} {
            set pin [lindex $pmod_jc $i]
            set net2pin(dout[$i]) $pin
        }
    } elseif {$pincfg eq "ARTY-A7-UART"} {
        # https://reference.digilentinc.com/reference/programmable-logic/arty/reference-manual?redirect=1
        # RST button and UART_RX
        set arty_in  "C2 A9"
        # LD7 and UART_TX
        set arty_out "T10 D10"

        # 100 MHz CLK onboard
        set pin "E3"
        set net2pin(clk) $pin

        # DIN
        for {set i 0} {$i < $DIN_N} {incr i} {
            set pin [lindex $arty_in $i]
            set net2pin(din[$i]) $pin
        }

        # DOUT
        for {set i 0} {$i < $DOUT_N} {incr i} {
            set pin [lindex $arty_out $i]
            set net2pin(dout[$i]) $pin
        }
    } else {
        error "Unsupported config $pincfg"
    }
} elseif {$part eq "xc7a35tcpg236-1"} {
    if {$pincfg eq "BASYS3-SWBUT"} {
        # https://raw.githubusercontent.com/Digilent/digilent-xdc/master/Basys-3-Master.xdc

        # Slide switches
        set ins "V17 V16 W16 W17 W15 V15 W14 W13 V2 T3 T2 R3 W2 U1 T1 R2"
        set outs "U16 E19 U19 V19 W18 U15 U14 V14 V13 V3 W3 U3 P3 N3 P1 L1"

        # UART
        lappend ins B18
        lappend outs A18


        # 100 MHz CLK onboard
        set pin "W5"
        set net2pin(clk) $pin

        # DIN
        for {set i 0} {$i < $DIN_N} {incr i} {
            set pin [lindex $ins $i]
            set net2pin(din[$i]) $pin
        }

        # DOUT
        for {set i 0} {$i < $DOUT_N} {incr i} {
            set pin [lindex $outs $i]
            set net2pin(dout[$i]) $pin
        }
    } else {
        error "Unsupported config $pincfg"
    }
} elseif {$part eq "xc7z010clg400-1"} {
    if {$pincfg eq "ZYBOZ7-SWBUT"} {
        # https://github.com/Digilent/digilent-xdc/blob/master/Zybo-Z7-Master.xdc

        #
        # J15 - UART_RX - JE3
        # G15 - SW0
        # K18 - BTN0
        # K19 - BTN1
        #
        set ins  "J15  G15  K18 K19"

        #
        # H15 - UART_TX - JE4
        # E17 - ETH PHY reset (active low, keep high for 125 MHz clock)
        # M14 - LD0
        # G14 - LD2
        # M15 - LD1
        # D18 - LD3
        #
        set outs "H15  E17  M14 M15 D18 G14"

        # 125 MHz CLK onboard
        set pin "K17"
        set net2pin(clk) $pin

        # DIN
        for {set i 0} {$i < $DIN_N} {incr i} {
            set pin [lindex $ins $i]
            set net2pin(din[$i]) $pin
        }

        # DOUT
        for {set i 0} {$i < $DOUT_N} {incr i} {
            set pin [lindex $outs $i]
            set net2pin(dout[$i]) $pin
        }

        # setting Y_OFFSET to zero only for zynq parts
        set Y_OFFSET 0

    } else {
        error "Unsupported config $pincfg"
    }
} else {
    error "Pins: unsupported part $part"
}

# Now actually apply the pin definitions
puts "Applying pin definitions"
foreach {net pin} [array get net2pin] {
    puts "  Net $net to pin $pin"
    set_property -dict "PACKAGE_PIN $pin IOSTANDARD LVCMOS33" [get_ports $net]
}

if {$fixed_xdc eq ""} {
    create_pblock roi
    set_property EXCLUDE_PLACEMENT 1 [get_pblocks roi]
    set_property CONTAIN_ROUTING true [get_pblocks roi]
    set_property DONT_TOUCH true [get_cells roi]
    add_cells_to_pblock [get_pblocks roi] [get_cells roi]
    resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    #set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

    set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]

    #write_checkpoint -force synth.dcp
}


proc loc_roi_clk_left {ff_x ff_y} {
    # Place an ROI clk on the left edge of the ROI
    # It doesn't actually matter where we place this, just do it to keep things neat looking
    # ff_x: ROI SLICE X position
    # ff_yy: row primitives will be placed at

    set slice_ff "SLICE_X${ff_x}Y${ff_y}"

    # Fix FFs to guide route in
    set cell [get_cells "roi/clk_reg_reg"]
    set_property LOC $slice_ff $cell
    set_property BEL AFF $cell
}

proc loc_lut_in {index lut_x lut_y} {
    # Place a lut at specified coordinates in BEL A
    # index: input bus index
    # lut_x: SLICE X position
    # lut_y: SLICE Y position

    set slice_lut "SLICE_X${lut_x}Y${lut_y}"

    # Fix LUTs near the edge
    set cell [get_cells "roi/ins[$index].lut"]
    set_property LOC $slice_lut $cell
    set_property BEL A6LUT $cell
}

proc loc_lut_out {index lut_x lut_y} {
    # Place a lut at specified coordinates in BEL A
    # index: input bus index
    # lut_x: SLICE X position
    # lut_y: SLICE Y position

    set slice_lut "SLICE_X${lut_x}Y${lut_y}"

    # Fix LUTs near the edge
    set cell [get_cells "roi/outs[$index].lut"]
    set_property LOC $slice_lut $cell
    set_property BEL A6LUT $cell
}

proc net_bank_left {net} {
    # return 1 if net goes to a leftmost die IO bank
    # return 0 if net goes to a rightmost die IO bank

    set bank [get_property IOBANK [get_ports $net]]
    set left_banks "14 15 16"
    set right_banks "34 35"

    # left
    if {[lsearch -exact $left_banks $bank] >= 0} {
        return 1
        # right
    } elseif {[lsearch -exact $right_banks $bank] >= 0} {
        return 0
    } else {
        error "Bad bank $bank"
    }
}

# Manual placement
if {$fixed_xdc eq ""} {
    set x $X_BASE

    # Place ROI clock right after inputs
    puts "Placing ROI clock"
    loc_roi_clk_left $x $Y_CLK_BASE

    # Place ROI inputs
    puts "Placing ROI inputs"
    set y_left $Y_DIN_BASE
    # Shift y_right up to avoid PCIe block that makes routing hard.
    set y_right [expr {$Y_DIN_BASE + $Y_OFFSET}]
    for {set i 0} {$i < $DIN_N} {incr i} {
        if {[net_bank_left "din[$i]"]} {
            loc_lut_in $i $XRAY_ROI_X0 $y_left
            set y_left [expr {$y_left + $PITCH}]
        } else {
            loc_lut_in $i $XRAY_ROI_X1 $y_right
            set y_right [expr {$y_right + $PITCH}]
        }
    }

    # Place ROI outputs
    set y_left $Y_DOUT_BASE
    set y_right $Y_DOUT_BASE
    puts "Placing ROI outputs"
    for {set i 0} {$i < $DOUT_N} {incr i} {
        if {[net_bank_left "dout[$i]"]} {
            loc_lut_out $i $XRAY_ROI_X0 $y_left
            set y_left [expr {$y_left + $PITCH}]
        } else {
            loc_lut_out $i $XRAY_ROI_X1 $y_right
            set y_right [expr {$y_right + $PITCH}]
        }
    }
}

place_design
#write_checkpoint -force placed.dcp

# Version with more error checking for missing end node
# Will do best effort in this case
proc route_via2 {net nodes} {
    # net: net as string
    # nodes: string list of one or more intermediate routing nodes to visit

    set net [get_nets $net]
    # Start at the net source
    set fixed_route [get_nodes -of_objects [get_site_pins -filter {DIRECTION == OUT} -of_objects $net]]
    # End at the net destination
    # For sone reason this doesn't always show up
    set site_pins [get_site_pins -filter {DIRECTION == IN} -of_objects $net]
    if {$site_pins eq ""} {
        puts "WARNING: could not find end node"
        #error "Could not find end node"
    } else {
        set end_node [get_nodes -of_objects]
        lappend nodes [$end_node]
    }

    puts ""
    puts "Routing net $net:"

    foreach to_node $nodes {
        if {$to_node eq ""} {
            error "Empty node"
        }

        # Node string to object
        set to_node [get_nodes -of_objects [get_wires $to_node]]
        # Start at last routed position
        set from_node [lindex $fixed_route end]
        # Let vivado do heavy liftin in between
        set route [find_routing_path -quiet -from $from_node -to $to_node]
        if {$route == ""} {
            # Some errors print a huge route
            puts [concat [string range "  $from_node -> $to_node" 0 1000] ": no route found - assuming direct PIP"]
            lappend fixed_route $to_node
        } {
            puts [concat [string range "  $from_node -> $to_node: $route" 0 1000] "routed"]
            set fixed_route [concat $fixed_route [lrange $route 1 end]]
        }
        set_property -quiet FIXED_ROUTE $fixed_route $net
    }

    set_property -quiet FIXED_ROUTE $fixed_route $net
    puts ""
}

# Return the wire on the ROI boundary
proc node2wire {node} {
    set wires [get_wires -of_objects [get_nodes $node]]
    set wire [lsearch -inline $wires *VBRK*]
    return $wire
}

proc write_grid_roi {fp} {
    puts $fp "GRID_X_MIN = $::env(XRAY_ROI_GRID_X1)"
    puts $fp "GRID_X_MAX = $::env(XRAY_ROI_GRID_X2)"
    puts $fp "GRID_Y_MIN = $::env(XRAY_ROI_GRID_Y1)"
    puts $fp "GRID_Y_MAX = $::env(XRAY_ROI_GRID_Y2)"
}

set fp [open "design_info.txt" w]
write_grid_roi $fp
close $fp

# XXX: maybe add IOB?
set fp [open "design.txt" w]
set fp_wires [open "design_pad_wires.txt" w]
puts $fp "name node pin wire"
# Manual routing
if {$fixed_xdc eq ""} {
    set x $X_BASE

    # No routing strictly needed for clk
    # It will go to high level interconnect that goes everywhere
    # But we still need to record something, so lets force a route
    # FIXME: very ROI specific
    set node "$XRAY_ROI_HCLK"
    set wire [node2wire $node]
    route_via2 "clk_IBUF_BUFG" "$node"
    set net "clk"
    set pin "$net2pin($net)"
    puts $fp "$net $node $pin $wire"

    puts "Routing ROI inputs"
    # Arbitrary offset as observed
    set y_left $Y_DIN_BASE
    set y_right [expr {$Y_DIN_BASE + $Y_OFFSET}]
    for {set i 0} {$i < $DIN_N} {incr i} {
        # needed to force routes away to avoid looping into ROI
        if {[net_bank_left "din[$i]"]} {
            set node "INT_L_X${DIN_INT_L_X}Y${y_left}/${DIN_LPIP}"
            route_via2 "din_IBUF[$i]" "$node"
            set y_left [expr {$y_left + $PITCH}]
        } else {
            set node "INT_R_X${DIN_INT_R_X}Y${y_right}/${DIN_RPIP}"
            route_via2 "din_IBUF[$i]" "$node"
            set y_right [expr {$y_right + $PITCH}]
        }
        set net "din[$i]"
        set pin "$net2pin($net)"
        set wire [node2wire $node]
        puts $fp "$net $node $pin $wire"

        set wires [get_wires -of_objects [get_nets "din_IBUF[$i]"]]
        puts $fp_wires "$net $pin $wires"
    }

    puts "Routing ROI outputs"
    # Arbitrary offset as observed
    set y_left [expr {$Y_DOUT_BASE + 0}]
    set y_right [expr {$Y_DOUT_BASE + 0}]
    for {set i 0} {$i < $DOUT_N} {incr i} {
        if {[net_bank_left "dout[$i]"]} {
            set node "INT_L_X${DOUT_INT_L_X}Y${y_left}/${DOUT_LPIP}"
            route_via2 "roi/dout[$i]" "$node"
            set y_left [expr {$y_left + $PITCH}]
            # XXX: only care about right ports on Arty
        } else {
            set node "INT_R_X${DOUT_INT_R_X}Y${y_right}/${DOUT_RPIP}"
            route_via2 "roi/dout[$i]" "$node"
            set y_right [expr {$y_right + $PITCH}]
        }
        set net "dout[$i]"
        set pin "$net2pin($net)"
        set wire [node2wire $node]
        puts $fp "$net $node $pin $wire"

        set wires [get_wires -of_objects [get_nets "roi/dout[$i]"]]
        puts $fp_wires "$net $pin $wires"
    }
}
close $fp
close $fp_wires

puts "routing design"
route_design

# Don't set for user designs
# Makes things easier to debug
if {$fixed_xdc eq ""} {
    set_property IS_ROUTE_FIXED 1 [get_nets -hierarchical]
    #set_property IS_LOC_FIXED 1 [get_cells -hierarchical]
    #set_property IS_BEL_FIXED 1 [get_cells -hierarchical]
    write_xdc -force fixed.xdc
}

write_checkpoint -force design.dcp
#set_property BITSTREAM.GENERAL.DEBUGBITSTREAM YES [current_design]
write_bitstream -force design.bit
