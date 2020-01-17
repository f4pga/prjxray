set blocknb [lindex $argv 0]
set start [expr int([lindex $argv 1])]
set stop [expr int([lindex $argv 2])]

create_project -force -part $::env(XRAY_PART) $blocknb $blocknb
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

#set_param tcl.collectionResultDisplayLimit 0
set_param messaging.disableStorage 1

set root_fp [open "root_${blocknb}.csv" w]
#puts $root_fp "filetype,subtype,filename"

set tiles [get_tiles]

create_pblock exclude_roi
foreach roi "$::env(XRAY_EXCLUDE_ROI_TILEGRID)" {
puts "ROI: $roi"
resize_pblock [get_pblocks exclude_roi] -add "$roi"
}

set not_allowed_sites [get_sites -of_objects [get_pblocks exclude_roi]]
set not_allowed_tiles [get_tiles -of_objects $not_allowed_sites]

# Convert DRIVE from ??? units to 10^(-3 to -6) Ohms
set MAGIC 0.6875

set speed_model_index_map [dict create]
set speed_model_name_map [dict create]

proc lookup_speed_model_index {index} {
    upvar speed_model_index_map speed_model_index_map
    if { ![dict exists $speed_model_index_map $index] } {
        set model [get_speed_models -filter "SPEED_INDEX == $index"]
        dict set speed_model_index_map $index $model
    }
    return [dict get $speed_model_index_map $index]
}

proc lookup_speed_model_name {name} {
    upvar speed_model_name_map speed_model_name_map
    if { ![dict exists $speed_model_name_map $name] } {
        set model [get_speed_models -filter "NAME == $name"]
        dict set speed_model_name_map $name $model
    }

    return [dict get $speed_model_name_map $name]
}

for {set j $start } { $j < $stop } { incr j } {

    set tile [lindex $tiles $j]

    # If tile is not allowed, skip it
    set res [lsearch $not_allowed_tiles $tile]
    if { $res != -1 } {
        continue
    }

    set fname tile_$tile.json5
    set tile_type [get_property TYPE $tile]
    puts $root_fp "tile,$tile_type,$fname"

    set fp [open "${fname}" w]
    puts $fp "\{"
    puts $fp "\t\"tile\": \"$tile\","
    # tile properties:
    # CLASS COLUMN DEVICE_ID FIRST_SITE_ID GRID_POINT_X GRID_POINT_Y INDEX
    # INT_TILE_X INT_TILE_Y IS_CENTER_TILE IS_DCM_TILE IS_GT_CLOCK_SITE_TILE
    # IS_GT_SITE_TILE NAME NUM_ARCS NUM_SITES ROW SLR_REGION_ID
    # TILE_PATTERN_IDX TILE_TYPE TILE_TYPE_INDEX TILE_X TILE_Y TYPE
    puts $fp "\t\"type\": \"$tile_type\","
    puts $fp "\t\"x\": [get_property GRID_POINT_X $tile],"
    puts $fp "\t\"y\": [get_property GRID_POINT_Y $tile],"
    puts $fp "\t\"sites\": \["
    foreach site [get_sites -of_objects $tile] {
        # site properties:
        # ALTERNATE_SITE_TYPES CLASS CLOCK_REGION IS_BONDED IS_CLOCK_BUFFER
        # IS_CLOCK_PAD IS_GLOBAL_CLOCK_BUFFER IS_GLOBAL_CLOCK_PAD IS_PAD
        # IS_REGIONAL_CLOCK_BUFFER IS_REGIONAL_CLOCK_PAD IS_RESERVED IS_TEST
        # IS_USED MANUAL_ROUTING NAME NUM_ARCS NUM_BELS NUM_INPUTS NUM_OUTPUTS
        # NUM_PINS PRIMITIVE_COUNT PROHIBIT PROHIBIT_FROM_PERSIST RPM_X RPM_Y
        # SITE_PIPS SITE_TYPE

        puts $fp "\t\t\{"
        puts $fp "\t\t\t\"site\":\"$site\","
        puts $fp "\t\t\t\"type\":\"[get_property SITE_TYPE $site]\","
        puts $fp "\t\t\t\"site_pins\": \["
        foreach site_pin [get_site_pins -of_objects $site] {
            # site_pin properties:
            # CLASS DIRECTION INDEX INDEX_IN_BUS INDEX_IN_SITE INDEX_IN_TILE IS_BAD
            # IS_INPUT IS_OUTPUT IS_PART_OF_BUS IS_TEST IS_USED NAME SITE_ID
            # SPEED_INDEX
            puts $fp "\t\t\t\{"
            puts $fp "\t\t\t\t\"site_pin\":\"$site_pin\","
            set site_pin_speed_model [lookup_speed_model_index [get_property SPEED_INDEX $site_pin]]
            set dir [get_property DIRECTION $site_pin]

            if { $dir == "IN" } {
                puts $fp "\t\t\t\t\"cap\": \"[get_property CAP $site_pin_speed_model]\","
            } else {
                set site_pin_speed_model [lookup_speed_model_name [get_property DRIVER $site_pin_speed_model]]
                puts $fp "\t\t\t\t\"res\": \"[expr $MAGIC * [get_property DRIVE $site_pin_speed_model]]\","
            }

            puts $fp "\t\t\t\t\"delay\": \["
            puts $fp "\t\t\t\t\t\"[get_property FAST_MIN $site_pin_speed_model]\","
            puts $fp "\t\t\t\t\t\"[get_property FAST_MAX $site_pin_speed_model]\","
            puts $fp "\t\t\t\t\t\"[get_property SLOW_MIN $site_pin_speed_model]\","
            puts $fp "\t\t\t\t\t\"[get_property SLOW_MAX $site_pin_speed_model]\","
            puts $fp "\t\t\t\t\],"
            puts $fp "\t\t\t\t\"direction\":\"$dir\","
            set site_pin_node [get_nodes -of_objects $site_pin]
            if {[llength $site_pin_node] == 0} {
                puts $fp "\t\t\t\t\"node\":null,"
            } else {
                puts $fp "\t\t\t\t\"node\":\"$site_pin_node\","
            }
            puts $fp "\t\t\t\},"
        }
        puts $fp "\t\t\t\],"
        puts $fp "\t\t\t\"site_pips\": \["
        foreach site_pip [get_site_pips -of_objects $site] {
            puts $fp "\t\t\t\{"
            # site_pips properties:
            # CLASS FROM_PIN IS_FIXED IS_USED NAME SITE TO_PIN
            puts $fp "\t\t\t\t\"site_pip\":\"$site_pip\","
            puts $fp "\t\t\t\t\"to_pin\":\"[get_property TO_PIN $site_pip]\","
            puts $fp "\t\t\t\t\"from_pin\":\"[get_property FROM_PIN $site_pip]\","
            puts $fp "\t\t\t\},"
        }
        puts $fp "\t\t\t\],"

        puts $fp "\t\t\t\"package_pins\": \["
        foreach package_pin [get_package_pins -of_objects $site] {
            puts $fp "\t\t\t\t\{"
            puts $fp "\t\t\t\t\t\"package_pin\":\"$package_pin\","
            puts $fp "\t\t\t\t\},"
        }
        puts $fp "\t\t\t\],"

        puts $fp "\t\t\},"
    }
    puts $fp "\t\],"
    puts $fp "\t\"pips\": \["
    foreach pip [get_pips -of_objects $tile] {
        # pip properties:
        # CAN_INVERT CLASS IS_BUFFERED_2_0 IS_BUFFERED_2_1 IS_DIRECTIONAL
        # IS_EXCLUDED_PIP IS_FIXED_INVERSION IS_INVERTED IS_PSEUDO IS_SITE_PIP
        # IS_TEST_PIP NAME SPEED_INDEX TILE
        puts $fp "\t\t\{"
        puts $fp "\t\t\t\"pip\":\"$pip\","
        set pip_speed_model [lookup_speed_model_index [get_property SPEED_INDEX $pip]]
        set forward_speed_model [lookup_speed_model_name [get_property FORWARD $pip_speed_model]]
        set reverse_speed_model [lookup_speed_model_name [get_property REVERSE $pip_speed_model]]

        set forward_speed_model_type [get_property TYPE $forward_speed_model]
        set reverse_speed_model_type [get_property TYPE $reverse_speed_model]
        set is_pass_transistor [expr {"$forward_speed_model_type" == "pass_transistor"}]
        puts $fp "\t\t\t\"is_pass_transistor\":$is_pass_transistor,"

        if { !$is_pass_transistor } {
            puts $fp "\t\t\t\"forward_delay\":\["
            puts $fp "\t\t\t\t\"[get_property FAST_MIN $forward_speed_model]\","
            puts $fp "\t\t\t\t\"[get_property FAST_MAX $forward_speed_model]\","
            puts $fp "\t\t\t\t\"[get_property SLOW_MIN $forward_speed_model]\","
            puts $fp "\t\t\t\t\"[get_property SLOW_MAX $forward_speed_model]\","
            puts $fp "\t\t\t\],"
            if {$forward_speed_model_type == "buffer_switch" || $forward_speed_model_type == "buffer"} {
                puts $fp "\t\t\t\"forward_res\": \"[expr $MAGIC * [get_property DRIVE $forward_speed_model]]\","
            }
            if {$forward_speed_model_type == "buffer_switch"} {
                puts $fp "\t\t\t\"forward_in_cap\": \"[get_property IN_CAP $forward_speed_model]\","
            }

            puts $fp "\t\t\t\"reverse_delay\":\["
            puts $fp "\t\t\t\t\"[get_property FAST_MIN $reverse_speed_model]\","
            puts $fp "\t\t\t\t\"[get_property FAST_MAX $reverse_speed_model]\","
            puts $fp "\t\t\t\t\"[get_property SLOW_MIN $reverse_speed_model]\","
            puts $fp "\t\t\t\t\"[get_property SLOW_MAX $reverse_speed_model]\","
            puts $fp "\t\t\t\],"
            if {$reverse_speed_model_type == "buffer_switch" || $reverse_speed_model_type == "buffer"} {
                puts $fp "\t\t\t\"reverse_res\": \"[expr $MAGIC * [get_property DRIVE $reverse_speed_model]]\","
            }
            if {$reverse_speed_model_type == "buffer_switch"} {
                puts $fp "\t\t\t\"reverse_in_cap\": \"[get_property IN_CAP $reverse_speed_model]\","
            }
        } else {
            puts $fp "\t\t\t\"forward_res\": \"[get_property RES $forward_speed_model]\","
            puts $fp "\t\t\t\"reverse_res\": \"[get_property RES $reverse_speed_model]\","
        }
        puts $fp "\t\t\t\"src_wire\":\"[get_wires -uphill -of_objects $pip]\","
        puts $fp "\t\t\t\"dst_wire\":\"[get_wires -downhill -of_objects $pip]\","
        puts $fp "\t\t\t\"is_pseudo\":\"[get_property IS_PSEUDO $pip]\","
        puts $fp "\t\t\t\"is_directional\":\"[get_property IS_DIRECTIONAL $pip]\","
        puts $fp "\t\t\t\"can_invert\":\"[get_property CAN_INVERT $pip]\","
        puts $fp "\t\t\},"
    }
    puts $fp "\t\],"

    puts $fp "\t\"wires\": \["
    foreach wire [get_wires -of_objects $tile] {
        # wire properties:
        # CLASS COST_CODE ID_IN_TILE_TYPE IS_CONNECTED IS_INPUT_PIN IS_OUTPUT_PIN
        # IS_PART_OF_BUS NAME NUM_DOWNHILL_PIPS NUM_INTERSECTS NUM_PIPS
        # NUM_TILE_PORTS NUM_UPHILL_PIPS SPEED_INDEX TILE_NAME TILE_PATTERN_OFFSET
        puts $fp "\t\t\{"
        set wire_speed_model [lookup_speed_model_index [get_property SPEED_INDEX $wire]]
        puts $fp "\t\t\t\"wire\":\"$wire\","
        puts $fp "\t\t\t\"res\":\"[get_property WIRE_RES $wire_speed_model]\","
        puts $fp "\t\t\t\"cap\":\"[get_property WIRE_CAP $wire_speed_model]\","
        puts $fp "\t\t\},"
    }
    puts $fp "\t\],"
    puts $fp "\}"
    close $fp
}

close $root_fp
