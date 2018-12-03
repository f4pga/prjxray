proc make_project {} {
    create_project -force -part $::env(XRAY_PART) design design

    read_verilog "$::env(FUZDIR)/top.v"
    synth_design -top top

    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports di]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports do]
    set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports stb]

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


