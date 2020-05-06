# Copyright (C) 2017-2020  The Project X-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
open_checkpoint harness_synth.dcp

create_pblock roi
add_cells_to_pblock [get_pblocks roi] [get_cells roi]
resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]

# Number of package inputs going to ROI
set DIN_N 8
# Number of ROI outputs going to package
set DOUT_N 8

set part $::env(XRAY_PART)
set pincfg $::env(XRAY_PINCFG)

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
    # Arty A7 switch, button, and LED
    if {$pincfg eq "ARTY-A7-SWBUT"} {
        # https://reference.digilentinc.com/reference/programmable-logic/arty/reference-manual?redirect=1
        # 4 switches then 4 buttons
        set sw_but "A8 C11 C10 A10  D9 C9 B9 B8"
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
        # Arty A7 pmod
        # Disabled per above
    } elseif {$pincfg eq "ARTY-A7-PMOD"} {
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
    } else {
        error "Unsupported config $pincfg"
    }
} elseif {$part eq "xc7a35tcpg236-1"} {
    if {$pincfg eq "BASYS3-SWBUT"} {
        # https://raw.githubusercontent.com/Digilent/digilent-xdc/master/Basys-3-Master.xdc

        # Slide switches
        set sws "V17 V16 W16 W17 W15 V15 W14 W13 V2 T3 T2 R3 W2 U1 T1 R2"
        set leds "U16 E19 U19 V19 W18 U15 U14 V14 V13 V3 W3 U3 P3 N3 P1 L1"

        # 100 MHz CLK onboard
        set pin "W5"
        set net2pin(clk) $pin

        # DIN
        for {set i 0} {$i < $DIN_N} {incr i} {
            set pin [lindex $sws $i]
            set net2pin(din[$i]) $pin
        }

        # DOUT
        for {set i 0} {$i < $DOUT_N} {incr i} {
            set pin [lindex $leds $i]
            set net2pin(dout[$i]) $pin
        }
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

set_property HD.RECONFIGURABLE TRUE [get_cells roi]

read_checkpoint -cell roi inv_synth.dcp

opt_design
place_design
route_design

# Replace roi cell with a black box and write the rest of the design
update_design -cell roi -black_box
lock_design -level routing
write_checkpoint -force harness_impl.dcp
