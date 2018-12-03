proc make_ios {} {
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

    set iopad ""
    dict for {key value} $io_pad_sites {
        lappend iopad [lindex $value 0]
    }
    return $iopad
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
    set iopad [make_ios]
    # Basic pins
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
    # 6 CMTs in our reference part
    # What is the largest?
    set n_di 16

    create_project -force -part $::env(XRAY_PART) design design

    read_verilog "$::env(FUZDIR)/top.v"
    synth_design -top top -verilog_define N_DI=$n_di

    assign_iobs

    create_pblock roi
    add_cells_to_pblock [get_pblocks roi] [get_cells roi]
    foreach roi "$::env(XRAY_ROI_TILEGRID)" {
        puts "ROI: $roi"
        resize_pblock [get_pblocks roi] -add "$roi"
    }

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
    set_param tcl.collectionResultDisplayLimit 0

    set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]
}

