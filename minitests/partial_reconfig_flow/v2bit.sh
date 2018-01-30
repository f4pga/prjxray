set -ex

fin=$1
if [ -z "$fin" ] ; then
    echo "need fin arg"
    exit
fi
# fin=roi_blinky.v
prefix=$(echo $fin |sed "s/\.v//")
if [ "$fin" = "$prefix" ] ; then
    echo "bad prefix"
    exit
fi
echo "$fin => $prefix"

make
mkdir -p $prefix

vivado -mode batch -source /dev/stdin <<EOF
read_verilog $prefix.v
synth_design -mode out_of_context -top roi -part \$::env(XRAY_PART)
write_checkpoint -force $prefix.dcp

open_checkpoint harness_routed.dcp
read_checkpoint -cell roi $prefix.dcp
opt_design
place_design
route_design
write_checkpoint -force ${prefix}_routed.dcp
write_bitstream -force ${prefix}_routed.bit
EOF

make ${prefix}_routed.fasm
make ${prefix}_routed.hand_crafted.bit

# Program
bit_fn=${prefix}_routed.hand_crafted.bit
openocd -f $XRAY_DIR/minitests/roi_harness/openocd-basys3.cfg -c "init; pld load 0 $bit_fn; exit"

