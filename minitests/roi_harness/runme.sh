#!/bin/bash

# 12x8 CLBs
if [ $SMALL = Y ] ; then
    echo "Design: small"
    export DIN_N=2
    export DOUT_N=2
    export XRAY_ROI=SLICE_X12Y100:SLICE_X27Y111
# 50x8 CLBs
else
    echo "Design: large"
    export DIN_N=8
    export DOUT_N=8
    export XRAY_ROI=SLICE_X12Y100:SLICE_X27Y149
fi

cat >defines.v <<EOF
\`ifndef DIN_N
\`define DIN_N $DIN_N
\`endif

\`ifndef DOUT_N
\`define DOUT_N $DOUT_N
\`endif
EOF


set -ex
rm -f out_last
vivado -mode batch -source runme.tcl
test -z "$(fgrep CRITICAL vivado.log)"

pushd out_last
${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design.bits -z -y design.bit
${XRAY_SEGPRINT} -zd design.bits >design.segp
${XRAY_DIR}/tools/segprint2fasm.py design.segp design.fasm
${XRAY_DIR}/tools/fasm2frame.py design.fasm design.frm
# Hack to get around weird clock error related to clk net not found
# Remove following lines:
#set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]
#set_property FIXED_ROUTE { { CLK_BUFG_BUFGCTRL0_O CLK_BUFG_CK_GCLK0 ... CLK_L1 CLBLM_M_CLK }  } [get_nets clk_net]
if [ -f fixed.xdc ] ; then
    cat fixed.xdc |fgrep -v 'CLOCK_DEDICATED_ROUTE FALSE' |fgrep -v 'set_property FIXED_ROUTE { { CLK_BUFG_BUFGCTRL0_O' >fixed_noclk.xdc
fi
popd
