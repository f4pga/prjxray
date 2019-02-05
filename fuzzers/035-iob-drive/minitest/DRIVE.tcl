source "$::env(SRC_DIR)/template.tcl"

# set vals "0 4 8 12 16 24"
# ERROR: [Common 17-69] Command failed: Illegal DRIVE_STRENGTH value '0' for standard 'LVCMOS33'.
# Legal values: 4, 8, 12, 16
set prop DRIVE
set port [get_ports do]
source "$::env(SRC_DIR)/sweep.tcl"
