#!/usr/bin/env bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

# This script requires an XC7A50T family part

set -ex

source ${XRAY_DIR}/utils/environment.sh

export XRAY_PINCFG=${XRAY_PINCFG:-ARTY-A7-SWBUT}
export BUILD_DIR=${BUILD_DIR:-build}

# not part of the normal DB
# to generate:
cat >/dev/null <<EOF
pushd ${XRAY_DIR}
source minitests/roi_harness/basys3.sh
pushd fuzzers/001-part-yaml
make clean
make
make pushdb
popd
popd
EOF
stat ${XRAY_PART_YAML} >/dev/null

# 6x by 18y CLBs (108)
if [ "$SMALL" = Y ] ; then
    echo "Design: small"
    export PITCH=${XRAY_PITCH:-1}
    export DIN_N=${XRAY_DIN_N_SMALL:-8}
    export DOUT_N=${XRAY_DOUT_N_SMALL:-8}
    export XRAY_ROI=${XRAY_ROI_SMALL:-SLICE_X12Y100:SLICE_X17Y117}
# All of CMT X0Y2
else
    echo "Design: large"
    export PITCH=${XRAY_PITCH:-2}
    export DIN_N=${XRAY_DIN_N_LARGE:-8}
    export DOUT_N=${XRAY_DOUT_N_LARGE:-8}
    export XRAY_ROI=${XRAY_ROI_LARGE:-SLICE_X0Y100:SLICE_X35Y149}
fi

echo ${DIN_N}
echo ${DOUT_N}
echo ${XRAY_ROI}

mkdir -p $BUILD_DIR
pushd $BUILD_DIR

cat >defines.v <<EOF
\`ifndef DIN_N
\`define DIN_N $DIN_N
\`endif

\`ifndef DOUT_N
\`define DOUT_N $DOUT_N
\`endif
EOF

${XRAY_VIVADO} -mode batch -source ../runme.tcl
test -z "$(fgrep CRITICAL vivado.log)"

${XRAY_BITREAD} -F $XRAY_ROI_FRAMES -o design.bits -z -y design.bit
python3 ${XRAY_DIR}/utils/bit2fasm.py --verbose design.bit > design.fasm
python3 ${XRAY_DIR}/utils/fasm2frames.py design.fasm design.frm
PYTHONPATH=$PYTHONPATH:$XRAY_DIR/utils python3 ../create_design_json.py \
    --design_info_txt design_info.txt \
    --design_txt design.txt \
    --pad_wires design_pad_wires.txt \
    --design_fasm design.fasm > design.json

# Hack to get around weird clock error related to clk net not found
# Remove following lines:
#set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]
#set_property FIXED_ROUTE { { CLK_BUFG_BUFGCTRL0_O CLK_BUFG_CK_GCLK0 ... CLK_L1 CLBLM_M_CLK }  } [get_nets clk_net]
if [ -f fixed.xdc ] ; then
    cat fixed.xdc |fgrep -v 'CLOCK_DEDICATED_ROUTE FALSE' |fgrep -v 'set_property FIXED_ROUTE { { CLK_BUFG_BUFGCTRL0_O' >fixed_noclk.xdc
fi
popd
