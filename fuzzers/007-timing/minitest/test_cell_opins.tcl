# Demonstrates that cells can have 0 to 2 BEL output pins
# roi/dout_shr_reg[0]: roi/dout_shr[0]_i_1/O roi/dout_shr_reg[0]

set TIME_start [clock clicks -milliseconds]
set site_src_nets 0
set neti 0
set nets [get_nets -hierarchical]
set nnets [llength $nets]
set opins_zero 0
set opins_multi 0
foreach net $nets {
    incr neti
    puts "Net $neti / $nnets: $net"

    set out_pins [get_pins -filter {DIRECTION == OUT} -of_objects $net]
    set npins [llength $out_pins]
    if {$npins == 0} {
        puts "    $net zero source pins: $src_pin"
        incr opins_zero
    }
    if {$npins > 1} {
        puts "    $net multi source pins: $src_pin"
        incr opins_multi
    }
}
set TIME_taken [expr [clock clicks -milliseconds] - $TIME_start]
puts "Took ms: $TIME_taken"
puts "Result: $opins_zero / $nnets zero"
puts "Result: $opins_multi / $nnets multi"
