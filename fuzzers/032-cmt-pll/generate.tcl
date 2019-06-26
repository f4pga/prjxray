create_project -force -part $::env(XRAY_PART) design design
read_verilog top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

create_clock -period 10.00 [get_ports clk]


set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]
# Disable MMCM frequency etc sanity checks
set_property IS_ENABLED 0 [get_drc_checks {PDRC-29}]
set_property IS_ENABLED 0 [get_drc_checks {PDRC-30}]
set_property IS_ENABLED 0 [get_drc_checks {AVAL-50}]
set_property IS_ENABLED 0 [get_drc_checks {AVAL-53}]
set_property IS_ENABLED 0 [get_drc_checks {REQP-126}]
# PLL
set_property IS_ENABLED 0 [get_drc_checks {PDRC-43}]
set_property IS_ENABLED 0 [get_drc_checks {REQP-161}]
set_property IS_ENABLED 0 [get_drc_checks {AVAL-78}]

place_design
route_design

write_checkpoint -force design.dcp
write_bitstream -force design.bit

set fp [open params.json "w"]
puts $fp "\["
foreach cell [get_cells -hierarchical -filter {REF_NAME == PLLE2_ADV}] {
    puts $fp " {"
    puts $fp "   \"tile\": \"[get_tiles -of [get_sites -of $cell]]\","
    puts $fp "   \"site\": \"[get_sites -of $cell]\","
    puts $fp "   \"params\": {"
    foreach prop [list_property $cell] {
        puts $fp "    \"$prop\": \"[get_property $prop $cell]\","
    }
    puts $fp "   }"
    puts $fp " },"

}
puts $fp "\]"
close $fp
