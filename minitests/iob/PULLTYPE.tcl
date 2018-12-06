source "$::env(SRC_DIR)/template.tcl"

set port [get_ports di]

set_property PULLTYPE "" $port
write_checkpoint -force design_NONE.dcp
write_bitstream -force design_NONE.bit

set vals "KEEPER PULLUP PULLDOWN"
foreach {val} $vals {
    set_property PULLTYPE $val $port
    write_checkpoint -force design_$val.dcp
    write_bitstream -force design_$val.bit
}
