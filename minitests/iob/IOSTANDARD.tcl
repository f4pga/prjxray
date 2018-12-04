source "$::env(SRC_DIR)/template.tcl"

set prop IOSTANDARD
set port [get_ports do]
source "$::env(SRC_DIR)/sweep.tcl"

