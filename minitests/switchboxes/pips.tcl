
proc tile_pip_report {fd tile_name} {
	set tile [get_tile $tile_name]
	set pips [get_pips -of_object $tile]
	set dsts [lsort -unique [get_wires -filter "TILE_NAME == $tile" -downhill -of_objects $pips]]

	puts $fd ""
	puts $fd "PIP Report for tile $tile"
	puts $fd "==================================="

	puts $fd ""
	puts $fd "PIPs that implement 1:1 connections"
	puts $fd "-----------------------------------"

	foreach dst $dsts {
		set dst_node [get_node -of_objects $dst]
		set dst_span [llength [get_tiles -of_objects $dst_node]]
		set pips [get_pips -filter "TILE == $tile" -uphill -of_objects $dst_node]
		if {[llength $pips] == 1} {
			puts $fd ""
			puts $fd "Destination Wire (Node, Span): $dst ($dst_node, $dst_span)"
			foreach pip $pips {
				set src [get_wires -uphill -of_objects $pip]
				set src_node [get_node -of_objects $src]
				set src_span [llength [get_tiles -of_objects $src_node]]
				puts $fd "     Source Wire (Node, Span): $src ($src_node, $src_span) via $pip"
			}
			foreach pip [get_pips -quiet -filter "TILE != $tile" -uphill -of_objects $dst_node] {
				puts $fd "           Outside Source PIP: $pip"
			}
		}
	}

	puts $fd ""
	puts $fd "PIPs that implement N:1 connections"
	puts $fd "-----------------------------------"

	foreach dst $dsts {
		set dst_node [get_node -of_objects $dst]
		set dst_span [llength [get_tiles -of_objects $dst_node]]
		set pips [get_pips -filter "TILE == $tile" -uphill -of_objects $dst_node]
		if {[llength $pips] != 1} {
			puts $fd ""
			puts $fd "Destination Wire (Node, Span): $dst ($dst_node, $dst_span)"
			foreach pip $pips {
				set src [get_wires -uphill -of_objects $pip]
				set src_node [get_node -of_objects $src]
				set src_span [llength [get_tiles -of_objects $src_node]]
				puts $fd "     Source Wire (Node, Span): $src ($src_node, $src_span) via $pip"
			}
			foreach pip [get_pips -quiet -filter "TILE != $tile" -uphill -of_objects $dst_node] {
				puts $fd "           Outside Source PIP: $pip"
			}
		}
	}

	puts $fd ""
	puts $fd ""
}

tile_pip_report [open "pips_clbll.txt" w] CLBLL_L_X12Y119
tile_pip_report [open   "pips_int.txt" w]   INT_L_X12Y119

