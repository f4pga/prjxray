set filename [lindex $argv 0]

create_project -force -part $::env(XRAY_PART) -name $filename
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

set_param messaging.disableStorage 1
set fp [open $filename r]
set file_data [read $fp]
close $fp

set fp [open $filename w]

set indices [split $file_data "\n"]

set MAGIC 0.6875

proc get_speed_model_name {name} {
    return [get_speed_models -filter "NAME == $name"]
}

puts $fp "\{"


foreach index $indices {
    if {$index == ""} {
        continue
    }

    set split_index [split $index ","]
    set resource [lindex $split_index 0]
    set resource_index [lindex $split_index 1]

    puts $fp "\t\"$resource_index\":"
    puts $fp "\t\t\{"

    if {$resource == "site_pin"} {
        # Getting all site_pin information
        set speed_model [get_speed_models -filter "SPEED_INDEX == $resource_index"]

        puts $fp "\t\t\t\"resource_name\": \"$resource\","

        set driver_speed_model_name [get_property DRIVER $speed_model]
        if {$driver_speed_model_name != ""} {
            set driver_speed_model [get_speed_model_name [get_property DRIVER $speed_model]]
            set RES [expr $MAGIC * [get_property DRIVE $driver_speed_model]]

            puts $fp "\t\t\t\"cap\":\"null\","
            puts $fp "\t\t\t\"res\":\"$RES\","

            set FAST_MIN [get_property FAST_MIN $driver_speed_model]
            set FAST_MAX [get_property FAST_MAX $driver_speed_model]
            set SLOW_MIN [get_property SLOW_MIN $driver_speed_model]
            set SLOW_MAX [get_property SLOW_MAX $driver_speed_model]
        } else {
            set CAP [get_property CAP $speed_model]
            puts $fp "\t\t\t\"cap\":\"$CAP\","
            puts $fp "\t\t\t\"res\":\"null\","

            set FAST_MIN [get_property FAST_MIN $speed_model]
            set FAST_MAX [get_property FAST_MAX $speed_model]
            set SLOW_MIN [get_property SLOW_MIN $speed_model]
            set SLOW_MAX [get_property SLOW_MAX $speed_model]

        }

        puts $fp "\t\t\t\"fast_min\":\"$FAST_MIN\","
        puts $fp "\t\t\t\"fast_max\":\"$FAST_MAX\","
        puts $fp "\t\t\t\"slow_min\":\"$SLOW_MIN\","
        puts $fp "\t\t\t\"slow_max\":\"$SLOW_MAX\""
    } elseif {$resource == "pip"} {
        # Getting all site_pin information
        set speed_model [get_speed_models -filter "SPEED_INDEX == $resource_index"]

        puts $fp "\t\t\t\"resource_name\": \"$resource\","

        set forward_speed_model [get_speed_model_name [get_property FORWARD $speed_model]]
        set reverse_speed_model [get_speed_model_name [get_property REVERSE $speed_model]]

        set forward_speed_model_type [get_property TYPE $forward_speed_model]
        set reverse_speed_model_type [get_property TYPE $reverse_speed_model]
        set is_pass_transistor [expr {"$forward_speed_model_type" == "pass_transistor"}]
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
    } elseif {$resource == "wire"} {
        # Getting all wire information
        set speed_model [get_speed_models -filter "SPEED_INDEX == $resource_index"]

        puts $fp "\t\t\t\"resource_name\": \"$resource\","
        puts $fp "\t\t\t\"res\":\"[get_property WIRE_RES $speed_model]\","
        puts $fp "\t\t\t\"cap\":\"[get_property WIRE_CAP $speed_model]\","
    } else {
        puts "STUFF TO READ $index $resource"
        exit 2
    }

    puts $fp "\t\t\},"
}

puts $fp "\}"

close $fp
