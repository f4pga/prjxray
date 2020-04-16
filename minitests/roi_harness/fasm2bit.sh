# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
# Example pre-req
# ./runme.sh
# XRAY_ROIV=roi_inv.v XRAY_FIXED_XDC=out_xc7a35tcpg236-1_BASYS3-SWBUT_roi_basev/fixed_noclk.xdc ./runme.sh

set -ex

fasm_in=$1
if [ -z "$fasm_in" ] ; then
    echo "need .fasm arg"
    exit
fi
bit_in=$2
if [ -z "$bit_in" ] ; then
    echo "need .bit arg"
    exit
fi
bit_out=$3
if [ -z "$bit_out" ] ; then
    bit_out=$(echo $fasm_in |sed s/.fasm/.bit/)
    if [ "$bit_out" = "$fasm_in" ] ; then
        echo "Expected fasm file"
        exit 1
    fi
fi

echo "Design .fasm: $fasm_in"
echo "Harness .bit: $bit_in"
echo "Out .bit: $bit_out"

${XRAY_FASM2FRAMES} --sparse $fasm_in roi_partial.frm

${XRAY_TOOLS_DIR}/xc7patch \
	--part_name ${XRAY_PART} \
	--part_file ${XRAY_PART_YAML} \
	--bitstream_file $bit_in \
	--frm_file roi_partial.frm \
	--output_file $bit_out

#openocd -f $XRAY_DIR/utils/openocd/board-digilent-basys3.cfg -c "init; pld load 0 $bit_out; exit"

