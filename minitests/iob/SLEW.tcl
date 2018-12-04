source "$::env(SRC_DIR)/template.tcl"

# set vals "SLOW MEDIUM FAST"
# ERROR: [Common 17-69] Command failed: Slew type 'MEDIUM' is not supported by I/O standard 'LVCMOS33'
set prop SLEW
set port [get_ports do]
source "$::env(SRC_DIR)/sweep.tcl"

