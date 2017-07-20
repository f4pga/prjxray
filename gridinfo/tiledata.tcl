
foreach tile [get_tiles] {
	foreach prop [list_property $tile] {
		puts "--tiledata-- TILEPROP $tile $prop [get_property $prop $tile]"
	}
	foreach site [get_sites -quiet -of_objects $tile] {
		puts "--tiledata-- TILESITE $tile $site"
	}
}

foreach site [get_sites] {
	foreach prop [list_property $site] {
		puts "--tiledata-- SITEPROP $site $prop [get_property $prop $site]"
	}
}

