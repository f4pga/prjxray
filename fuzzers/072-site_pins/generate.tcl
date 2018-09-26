# This script first finds a list of all tile types.  It then outputs all nodes
# within each tile, and any connected site_pins.  It also outputs all sites
# present within the tile, its site type, and the list of site pins.
#
# This information should be sufficent to map the tile routing resources to
# the sites within a tile.
#
# The output format is JSON5, which can be converted to JSON with json5.tool:
# python -mjson5.tool --json {input JSON5 file} > {output JSON file}.
# In particular, this tcl script leverages trailing comma's for simplicity.
create_project -force -part $::env(XRAY_PART) design design

read_verilog ../top.v
synth_design -top top

set tilelist [get_tiles]
set prototype_tiles [dict create]
foreach tile $tilelist {
  set tile_type [get_property type $tile]
  if {![dict exists $prototype_tiles $tile_type]} {
    dict set prototype_tiles $tile_type $tile
  }
}

dict for {tile_type tile} $prototype_tiles {
  set tile_channel [open site_pins_$tile_type.json5 w]

  set tile_name [get_property name $tile]
  puts $tile_channel "\{"
  puts $tile_channel "\t\"tile_name\": \"$tile_name\","
  puts $tile_channel "\t\"tile_type\": \"$tile_type\","

  set nodes [get_nodes -of_objects $tile]
  puts $tile_channel "\t\"nodes\": \["
  foreach node $nodes {
    set site_pins [get_site_pins -of_objects $node]
    set wires [get_wires -of_objects $node]
    puts $tile_channel "\t\t\{"
    puts $tile_channel "\t\t\t\"node\": \"$node\","
    puts $tile_channel "\t\t\t\"site_pins\": \["
    foreach site_pin $site_pins {
      puts $tile_channel "\t\t\t\t\"$site_pin\","
    }
    puts $tile_channel "\t\t\t\],"
    puts $tile_channel "\t\t\t\"wires\": \["
    foreach wire $wires {
      puts $tile_channel "\t\t\t\t\"$wire\","
    }
    puts $tile_channel "\t\t\t\]"
    puts $tile_channel "\t\t\},"
  }
  puts $tile_channel "\t\],"

  set sites [get_sites -of_objects $tile]
  puts $tile_channel "\t\"sites\": \["
  foreach site $sites {
    set site_pins [get_site_pins -of_object $site]
    set site_type [get_property site_type $site]
    set site_name [get_property name $site]
    puts $tile_channel "\t\t\{"
    puts $tile_channel "\t\t\t\"name\": \"$site_name\","
    puts $tile_channel "\t\t\t\"type\": \"$site_type\","
    puts $tile_channel "\t\t\t\"site_pins\": \["
    foreach site_pin $site_pins {
      set site_pin_direction [get_property direction $site_pin]
      puts $tile_channel "\t\t\t\t\{\"name\": \"$site_pin\", \"direction\": \"$site_pin_direction\"\},"
    }
    puts $tile_channel "\t\t\t\]"
    puts $tile_channel "\t\t\},"
  }
  puts $tile_channel "\t\]"

  puts $tile_channel "\}"

  close $tile_channel
}
