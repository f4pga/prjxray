proc puts_list {l} {
	foreach e $l {puts $e}
}

proc get_carry_cyinit_mux_cfg {carry_cell} {
	set cyinit_pin [get_pins -of_objects $carry_cell -filter {REF_PIN_NAME == CYINIT}]
	set cyinit_net [get_nets -quiet -of_objects $cyinit_pin]

	if {[string last "<const0>" $cyinit_net] > 0} { return "zro" }
	if {[string last "<const1>" $cyinit_net] > 0} { return "one" }

	set ax_pin [get_site_pins -of_objects [get_sites -of_objects $carry_cell] */AX]
	set ax_net [get_nets -quiet -of_objects $ax_pin]
	if {"$cyinit_net" == "$ax_net"} { return "ax " }

	set cin_pin [get_site_pins -of_objects [get_sites -of_objects $carry_cell] */CIN]
	set cin_net [get_nets -quiet -of_objects $cin_pin]
	if {"$cyinit_net" == "$cin_net"} { return "cin" }

	return "???"
}

proc get_carry_di0_mux_cfg {carry_cell} {
	set di0_pin [get_pins -of_objects $carry_cell -filter {REF_PIN_NAME == DI[0]}]
	set di0_net [get_nets -quiet -of_objects $di0_pin]

	set ax_pin [get_site_pins -of_objects [get_sites -of_objects $carry_cell] */AX]
	set ax_net [get_nets -quiet -of_objects $ax_pin]
	if {"$di0_net" == "$ax_net"} { return "ax " }

	return "o5 "
}

proc get_carry_di1_mux_cfg {carry_cell} {
	set di1_pin [get_pins -of_objects $carry_cell -filter {REF_PIN_NAME == DI[1]}]
	set di1_net [get_nets -quiet -of_objects $di1_pin]

	set bx_pin [get_site_pins -of_objects [get_sites -of_objects $carry_cell] */BX]
	set bx_net [get_nets -quiet -of_objects $bx_pin]
	if {"$di1_net" == "$bx_net"} { return "bx " }

	return "o5 "
}

proc get_carry_di2_mux_cfg {carry_cell} {
	set di2_pin [get_pins -of_objects $carry_cell -filter {REF_PIN_NAME == DI[2]}]
	set di2_net [get_nets -quiet -of_objects $di2_pin]

	set cx_pin [get_site_pins -of_objects [get_sites -of_objects $carry_cell] */CX]
	set cx_net [get_nets -quiet -of_objects $cx_pin]
	if {"$di2_net" == "$cx_net"} { return "cx " }

	return "o5 "
}

proc get_carry_di3_mux_cfg {carry_cell} {
	set di3_pin [get_pins -of_objects $carry_cell -filter {REF_PIN_NAME == DI[3]}]
	set di3_net [get_nets -quiet -of_objects $di3_pin]

	set dx_pin [get_site_pins -of_objects [get_sites -of_objects $carry_cell] */DX]
	set dx_net [get_nets -quiet -of_objects $dx_pin]
	if {"$di3_net" == "$dx_net"} { return "dx " }

	return "o5 "
}

proc list_carry_cfg {} {
	foreach carry_cell [get_cells -hierarchical -filter {REF_NAME == CARRY4}] {
		set cyinit_mux_cfg [get_carry_cyinit_mux_cfg $carry_cell]
		set di0_mux_cfg    [get_carry_di0_mux_cfg $carry_cell]
		set di1_mux_cfg    [get_carry_di1_mux_cfg $carry_cell]
		set di2_mux_cfg    [get_carry_di2_mux_cfg $carry_cell]
		set di3_mux_cfg    [get_carry_di3_mux_cfg $carry_cell]
		puts "[get_bels -of_objects $carry_cell] $cyinit_mux_cfg $di0_mux_cfg $di1_mux_cfg $di2_mux_cfg $di3_mux_cfg"
	}
}
