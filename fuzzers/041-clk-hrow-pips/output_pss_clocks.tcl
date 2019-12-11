create_project -force -part $::env(XRAY_PART) design design
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

set fp [open "pss_clocks.csv" "w"]
puts $fp "pin,tile"

# List all PSS_HCLK wires
set pss_clk_wires [get_wires *PSS_HCLK* -of_objects [get_tiles PSS*]]
foreach wire $pss_clk_wires {
    # Get PIPs that mention the wire inside a CLK_HROW tile.
    set pips [get_pips CLK_HROW_* -of_objects [get_nodes -of_objects $wire]]
    # Get the CLK_HROW tile.
    set tile [get_tiles -of_objects [lindex $pips 0]]

    # Get uphill PIP, parse its name to get the PS7 wire name.
    set pip [get_pips -uphill -of_objects $wire]
    set pin [lindex [split [lindex [split $pip "."] 1] "-"] 0]

    puts $fp "$pin,$tile"
}

close $fp
