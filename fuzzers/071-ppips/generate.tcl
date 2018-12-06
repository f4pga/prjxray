create_project -force -part $::env(XRAY_PART) design design

read_verilog ../top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports a]
set_property -dict "PACKAGE_PIN $::env(XRAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports y]

create_pblock roi
resize_pblock [get_pblocks roi] -add "$::env(XRAY_ROI)"

set_property CFGBVS VCCO [current_design]
set_property CONFIG_VOLTAGE 3.3 [current_design]
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
set_param tcl.collectionResultDisplayLimit 0

place_design
route_design

write_checkpoint -force design.dcp
# write_bitstream -force design.bit

proc write_clb_ppips_db {filename tile} {
    set fp [open $filename "w"]
    set tile [get_tiles $tile]
    set tile_type [get_property TILE_TYPE $tile]

    foreach pip [get_pips -of_objects $tile] {
        set dst_wire [get_wires -downhill -of_objects $pip]
        if {[get_property IS_PSEUDO $pip]} {
            set src_wire [get_wires -uphill -of_objects $pip]
            puts $fp "${tile_type}.[regsub {.*/} $dst_wire ""].[regsub {.*/} $src_wire ""] hint"
        } elseif {[get_pips -uphill -of_objects [get_nodes -of_objects $dst_wire]] == $pip} {
            set src_wire [get_wires -uphill -of_objects $pip]
            puts $fp "${tile_type}.[regsub {.*/} $dst_wire ""].[regsub {.*/} $src_wire ""] always"
        }
    }

    close $fp
}

proc write_int_ppips_db {filename tile} {
    set fp [open $filename "w"]
    set tile [get_tiles $tile]
    set tile_type [get_property TILE_TYPE $tile]

    foreach pip [get_pips -of_objects [get_wires $tile/VCC_WIRE]] {
        set wire [regsub {.*/} [get_wires -downhill -of_objects $pip] ""]
        puts $fp "${tile_type}.${wire}.VCC_WIRE default"
    }

    foreach pip [get_pips -of_objects $tile] {
        set dst_wire [get_wires -downhill -of_objects $pip]
        if {[get_pips -uphill -of_objects [get_nodes -of_objects $dst_wire]] == $pip} {
            set src_wire [get_wires -uphill -of_objects $pip]
            puts $fp "${tile_type}.[regsub {.*/} $dst_wire ""].[regsub {.*/} $src_wire ""] always"
        }
    }

    close $fp
}

foreach tile_type {CLBLM_L CLBLM_R CLBLL_L CLBLL_R INT_L INT_R} {
    set tiles [get_tiles -filter "TILE_TYPE == $tile_type"]
    if {[llength $tiles] != 0} {
        set tile [lindex $tiles 0]
        write_clb_ppips_db "ppips_[string tolower $tile_type].txt" $tile
    }
}
