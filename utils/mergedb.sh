#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

# $1: DB type
# $2: filename to merge in

set -ex
test $# = 2
test -e "$2"

tmp1=`mktemp -p .`
tmp2=`mktemp -p .`
LOCKFILE="/tmp/segbits_$1.db.lock"
LOCKTIMEOUT=30 # 30s timeout
LOCKID=222

function finish {
    echo "Cleaning up temp files"
    rm -f "$tmp1"
    rm -f "$tmp2"
}
trap finish EXIT

db=$XRAY_DATABASE_DIR/$XRAY_DATABASE/segbits_$1.db

# if the DB exists acquire a lock
if [ -f $db ]; then
	eval "exec $LOCKID>$LOCKFILE"
	# the lock is automatically released on script exit
	flock --timeout $LOCKTIMEOUT $LOCKID
	if [ ! $? -eq 0 ]; then
		echo "Timeout while waiting for lock"
		finish
		exit 1
	fi
fi

# Check existing DB
if [ -f $db ] ; then
    ${XRAY_PARSEDB} --strict "$db"
fi

# Check new DB
${XRAY_PARSEDB} --strict "$2"

# Fuzzers verify L/R data is equivilent
# However, expand back to L/R to make downstream tools not depend on this
# in case we later find exceptions

ismask=false
case "$1" in
	clbll_l)
		sed < "$2" > "$tmp1" \
			-e 's/^CLB\.SLICE_X0\./CLBLL_L.SLICEL_X0./' \
			-e 's/^CLB\.SLICE_X1\./CLBLL_L.SLICEL_X1./' ;;
	clbll_r)
		sed < "$2" > "$tmp1" \
			-e 's/^CLB\.SLICE_X0\./CLBLL_R.SLICEL_X0./' \
			-e 's/^CLB\.SLICE_X1\./CLBLL_R.SLICEL_X1./' ;;
	clblm_l)
		sed < "$2" > "$tmp1" \
			-e 's/^CLB\.SLICE_X0\./CLBLM_L.SLICEM_X0./' \
			-e 's/^CLB\.SLICE_X1\./CLBLM_L.SLICEL_X1./' ;;
	clblm_r)
		sed < "$2" > "$tmp1" \
			-e 's/^CLB\.SLICE_X0\./CLBLM_R.SLICEM_X0./' \
			-e 's/^CLB\.SLICE_X1\./CLBLM_R.SLICEL_X1./' ;;

	dsp_l)
		sed < "$2" > "$tmp1" -e 's/^DSP\./DSP_L./' ;;
	dsp_r)
		sed < "$2" > "$tmp1" -e 's/^DSP\./DSP_R./' ;;

	bram_l)
		sed < "$2" > "$tmp1" -e 's/^BRAM\./BRAM_L./' ;;
	bram_r)
		sed < "$2" > "$tmp1" -e 's/^BRAM\./BRAM_R./' ;;

	bram_l.block_ram)
		sed < "$2" > "$tmp1" -e 's/^BRAM\./BRAM_L./' ;;
	bram_r.block_ram)
		sed < "$2" > "$tmp1" -e 's/^BRAM\./BRAM_R./' ;;

	int_l)
		sed < "$2" > "$tmp1" -e 's/^INT\./INT_L./' ;;
	int_r)
		sed < "$2" > "$tmp1" -e 's/^INT\./INT_R./' ;;

	hclk_l)
		sed < "$2" > "$tmp1" -e 's/^HCLK\./HCLK_L./' ;;
	hclk_r)
		sed < "$2" > "$tmp1" -e 's/^HCLK\./HCLK_R./' ;;

	clk_hrow_bot_r)
		sed < "$2" > "$tmp1" -e 's/^CLK_HROW\./CLK_HROW_BOT_R./' ;;
	clk_hrow_top_r)
		sed < "$2" > "$tmp1" -e 's/^CLK_HROW\./CLK_HROW_TOP_R./' ;;

	clk_bufg_bot_r)
		sed < "$2" > "$tmp1" -e 's/^CLK_BUFG\./CLK_BUFG_BOT_R./' ;;
	clk_bufg_top_r)
		sed < "$2" > "$tmp1" -e 's/^CLK_BUFG\./CLK_BUFG_TOP_R./' ;;

	hclk_cmt)
		cp "$2" "$tmp1" ;;
	hclk_cmt_l)
		sed < "$2" > "$tmp1" -e 's/^HCLK_CMT\./HCLK_CMT_L./' ;;

	clk_bufg_rebuf)
		cp "$2" "$tmp1" ;;

	liob33)
		sed < "$2" > "$tmp1" -e 's/^IOB33\./LIOB33./' ;;

	riob33)
		sed < "$2" > "$tmp1" -e 's/^IOB33\./RIOB33./' ;;

	riob18)
		sed < "$2" > "$tmp1" -e 's/^IOB18\./RIOB18./' ;;

	lioi3)
		sed < "$2" > "$tmp1" -e 's/^IOI3\./LIOI3./' ;;

	lioi3_tbytesrc)
		sed < "$2" > "$tmp1" -e 's/^IOI3\./LIOI3_TBYTESRC./' ;;

	lioi3_tbyteterm)
		sed < "$2" > "$tmp1" -e 's/^IOI3\./LIOI3_TBYTETERM./' ;;

	rioi3)
		sed < "$2" > "$tmp1" -e 's/^IOI3\./RIOI3./' ;;

	rioi)
		sed < "$2" > "$tmp1" -e 's/^IOI\./RIOI./' ;;

	rioi3_tbytesrc)
		sed < "$2" > "$tmp1" -e 's/^IOI3\./RIOI3_TBYTESRC./' ;;

	rioi_tbytesrc)
		sed < "$2" > "$tmp1" -e 's/^IOI\./RIOI_TBYTESRC./' ;;

	rioi3_tbyteterm)
		sed < "$2" > "$tmp1" -e 's/^IOI3\./RIOI3_TBYTETERM./' ;;

	rioi_tbyteterm)
		sed < "$2" > "$tmp1" -e 's/^IOI\./RIOI_TBYTETERM./' ;;

	cmt_top_r_upper_t)
		sed < "$2" > "$tmp1" -e 's/^CMT_UPPER_T\./CMT_TOP_R_UPPER_T./' ;;

	cmt_top_l_upper_t)
		sed < "$2" > "$tmp1" -e 's/^CMT_UPPER_T\./CMT_TOP_L_UPPER_T./' ;;

	cmt_top_r_lower_b)
		sed < "$2" > "$tmp1" -e 's/^CMT_LOWER_B\./CMT_TOP_R_LOWER_B./' ;;

	cmt_top_l_lower_b)
		sed < "$2" > "$tmp1" -e 's/^CMT_LOWER_B\./CMT_TOP_L_LOWER_B./' ;;

	cfg_center_mid)
		cp "$2" "$tmp1" ;;

	hclk_ioi3)
		cp "$2" "$tmp1" ;;

	hclk_ioi)
		cp "$2" "$tmp1" ;;

	pcie_bot)
		cp "$2" "$tmp1" ;;

	pcie_int_interface_l)
		sed < "$2" > "$tmp1" -e 's/^PCIE_INT_INTERFACE\./PCIE_INT_INTERFACE_L./' ;;

	pcie_int_interface_r)
		sed < "$2" > "$tmp1" -e 's/^PCIE_INT_INTERFACE\./PCIE_INT_INTERFACE_R./' ;;

	gtp_common)
		cp "$2" "$tmp1" ;;

	gtp_common_mid_left)
		sed < "$2" > "$tmp1" -e 's/^GTP_COMMON\./GTP_COMMON_MID_LEFT./' ;;

	gtp_common_mid_right)
		sed < "$2" > "$tmp1" -e 's/^GTP_COMMON\./GTP_COMMON_MID_RIGHT./' ;;

	gtp_channel_0)
		sed < "$2" > "$tmp1" -e 's/^GTP_CHANNEL\./GTP_CHANNEL_0./' ;;

	gtp_channel_1)
		sed < "$2" > "$tmp1" -e 's/^GTP_CHANNEL\./GTP_CHANNEL_1./' ;;

	gtp_channel_2)
		sed < "$2" > "$tmp1" -e 's/^GTP_CHANNEL\./GTP_CHANNEL_2./' ;;

	gtp_channel_3)
		sed < "$2" > "$tmp1" -e 's/^GTP_CHANNEL\./GTP_CHANNEL_3./' ;;

	gtp_channel_0_mid_left)
		sed < "$2" > "$tmp1" -e 's/^GTP_CHANNEL\./GTP_CHANNEL_0_MID_LEFT./' ;;

	gtp_channel_1_mid_left)
		sed < "$2" > "$tmp1" -e 's/^GTP_CHANNEL\./GTP_CHANNEL_1_MID_LEFT./' ;;

	gtp_channel_2_mid_left)
		sed < "$2" > "$tmp1" -e 's/^GTP_CHANNEL\./GTP_CHANNEL_2_MID_LEFT./' ;;

	gtp_channel_3_mid_left)
		sed < "$2" > "$tmp1" -e 's/^GTP_CHANNEL\./GTP_CHANNEL_3_MID_LEFT./' ;;

	gtp_channel_0_mid_right)
		sed < "$2" > "$tmp1" -e 's/^GTP_CHANNEL\./GTP_CHANNEL_0_MID_RIGHT./' ;;

	gtp_channel_1_mid_right)
		sed < "$2" > "$tmp1" -e 's/^GTP_CHANNEL\./GTP_CHANNEL_1_MID_RIGHT./' ;;

	gtp_channel_2_mid_right)
		sed < "$2" > "$tmp1" -e 's/^GTP_CHANNEL\./GTP_CHANNEL_2_MID_RIGHT./' ;;

	gtp_channel_3_mid_right)
		sed < "$2" > "$tmp1" -e 's/^GTP_CHANNEL\./GTP_CHANNEL_3_MID_RIGHT./' ;;

	gtp_int_interface_l)
		sed < "$2" > "$tmp1" -e 's/^GTP_INT_INTERFACE\.GTPE2_INT/GTP_INT_INTERFACE_L\.GTPE2_INT_LEFT/' ;;

	gtp_int_interface_r)
		sed < "$2" > "$tmp1" -e 's/^GTP_INT_INTERFACE\.GTPE2_INT/GTP_INT_INTERFACE_R\.GTPE2_INT_R/' ;;

	gtp_int_interface)
		cp "$2" "$tmp1" ;;

	gtx_common)
		cp "$2" "$tmp1" ;;

	gtx_common_mid_left)
		sed < "$2" > "$tmp1" -e 's/^GTX_COMMON\./GTX_COMMON_MID_LEFT./' ;;

	gtx_common_mid_right)
		sed < "$2" > "$tmp1" -e 's/^GTX_COMMON\./GTX_COMMON_MID_RIGHT./' ;;

	gtx_channel_0)
		sed < "$2" > "$tmp1" -e 's/^GTX_CHANNEL\./GTX_CHANNEL_0./' ;;

	gtx_channel_1)
		sed < "$2" > "$tmp1" -e 's/^GTX_CHANNEL\./GTX_CHANNEL_1./' ;;

	gtx_channel_2)
		sed < "$2" > "$tmp1" -e 's/^GTX_CHANNEL\./GTX_CHANNEL_2./' ;;

	gtx_channel_3)
		sed < "$2" > "$tmp1" -e 's/^GTX_CHANNEL\./GTX_CHANNEL_3./' ;;

	gtx_channel_0_mid_left)
		sed < "$2" > "$tmp1" -e 's/^GTX_CHANNEL\./GTX_CHANNEL_0_MID_LEFT./' ;;

	gtx_channel_1_mid_left)
		sed < "$2" > "$tmp1" -e 's/^GTX_CHANNEL\./GTX_CHANNEL_1_MID_LEFT./' ;;

	gtx_channel_2_mid_left)
		sed < "$2" > "$tmp1" -e 's/^GTX_CHANNEL\./GTX_CHANNEL_2_MID_LEFT./' ;;

	gtx_channel_3_mid_left)
		sed < "$2" > "$tmp1" -e 's/^GTX_CHANNEL\./GTX_CHANNEL_3_MID_LEFT./' ;;

	gtx_channel_0_mid_right)
		sed < "$2" > "$tmp1" -e 's/^GTX_CHANNEL\./GTX_CHANNEL_0_MID_RIGHT./' ;;

	gtx_channel_1_mid_right)
		sed < "$2" > "$tmp1" -e 's/^GTX_CHANNEL\./GTX_CHANNEL_1_MID_RIGHT./' ;;

	gtx_channel_2_mid_right)
		sed < "$2" > "$tmp1" -e 's/^GTX_CHANNEL\./GTX_CHANNEL_2_MID_RIGHT./' ;;

	gtx_channel_3_mid_right)
		sed < "$2" > "$tmp1" -e 's/^GTX_CHANNEL\./GTX_CHANNEL_3_MID_RIGHT./' ;;

	gtx_int_interface_l)
		sed < "$2" > "$tmp1" -e 's/^GTX_INT_INTERFACE\.GTXE2_INT/GTX_INT_INTERFACE_L\.GTXE2_INT_LEFT/' ;;

	gtx_int_interface_r)
		sed < "$2" > "$tmp1" -e 's/^GTX_INT_INTERFACE\.GTXE2_INT/GTX_INT_INTERFACE_R\.GTXE2_INT_R/' ;;

	gtx_int_interface)
		cp "$2" "$tmp1" ;;

	mask_*)
		db=$XRAY_DATABASE_DIR/$XRAY_DATABASE/$1.db
		ismask=true
		cp "$2" "$tmp1" ;;

	*)
		echo "Invalid mode: $1"
		rm -f "$tmp1" "$tmp2"
		exit 1
esac

touch "$db"
if $ismask ; then
    sort -u "$tmp1" "$db" | grep -v '<.*>' > "$tmp2" || true
else
    # tmp1 must be placed second to take precedence over old bad entries
    if ! $ismask ; then
	db_origin=$XRAY_DATABASE_DIR/$XRAY_DATABASE/segbits_$1.origin_info.db
        if [ ! -f $db_origin ] ; then
            touch "$db_origin"
        fi
        python3 ${XRAY_DIR}/utils/mergedb.py --out "$db_origin" "$db_origin" "$tmp1" --track_origin
    fi
    python3 ${XRAY_DIR}/utils/mergedb.py --out "$tmp2" "$db" "$tmp1"
fi
# Check aggregate db for consistency and make canonical
${XRAY_PARSEDB} --strict "$tmp2" "$db"
