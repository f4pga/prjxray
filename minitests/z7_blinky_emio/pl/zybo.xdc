# LEDs
set_property PACKAGE_PIN M14 [get_ports led[0]]
set_property PACKAGE_PIN M15 [get_ports led[1]]
set_property PACKAGE_PIN G14 [get_ports led[2]]
set_property PACKAGE_PIN D18 [get_ports led[3]]

# Pushbuttons
set_property PACKAGE_PIN K18 [get_ports btn[0]]
set_property PACKAGE_PIN P16 [get_ports btn[1]]
set_property PACKAGE_PIN K19 [get_ports btn[2]]
set_property PACKAGE_PIN Y16 [get_ports btn[3]]

foreach port [get_ports] {
    set_property IOSTANDARD LVCMOS33 $port
    set_property SLEW SLOW $port
}

