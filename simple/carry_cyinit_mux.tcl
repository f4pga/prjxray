# set carry_cell [lindex [get_cells -hierarchical -filter {REF_NAME == CARRY4}] 0]

proc get_carry_cyinit_mux_cfg {carry_cell} {
	set cyinit_pin [get_pins -of_objects $carry_cell -filter {REF_PIN_NAME == CYINIT}]
	set cyinit_net [get_nets -quiet -of_objects $cyinit_pin]

	if {[string last "<const0>" $cyinit_net] > 0} { return "zero" }
	if {[string last "<const1>" $cyinit_net] > 0} { return "one" }

	set cin_pin [get_site_pins -of_objects [get_sites -of_objects $carry_cell] */CIN]
	set cin_net [get_nets -quiet -of_objects $cin_pin]
	if {"$cyinit_net" == "$cin_net"} { return "cin" }

	set ax_pin [get_site_pins -of_objects [get_sites -of_objects $carry_cell] */AX]
	set ax_net [get_nets -quiet -of_objects $ax_pin]
	if {"$cyinit_net" == "$ax_net"} { return "ax" }

	return "unknown"
}

proc list_carry_cyinit_mux_cfg {} {
	foreach carry_cell [get_cells -hierarchical -filter {REF_NAME == CARRY4}] {
		puts "[get_bels -of_objects $carry_cell] [get_carry_cyinit_mux_cfg $carry_cell]"
	}
}
