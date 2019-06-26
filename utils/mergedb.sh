#!/bin/bash

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

	cmt_top_r_upper_t)
		sed < "$2" > "$tmp1" -e 's/^CMT_UPPER_T\./CMT_TOP_R_UPPER_T./' ;;

	cmt_top_l_upper_t)
		sed < "$2" > "$tmp1" -e 's/^CMT_UPPER_T\./CMT_TOP_L_UPPER_T./' ;;

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
    python3 ${XRAY_DIR}/utils/mergedb.py --out "$tmp2" "$db" "$tmp1"
    if ! $ismask ; then
	db_origin=$XRAY_DATABASE_DIR/$XRAY_DATABASE/segbits_$1.origin_info.db
        if [ ! -f $db_origin ] ; then
            touch "$db_origin"
        fi
        python3 ${XRAY_DIR}/utils/mergedb.py --out "$db_origin" "$db_origin" "$tmp1" --track_origin
    fi
fi
# Check aggregate db for consistency and make canonical
${XRAY_PARSEDB} --strict "$tmp2" "$db"
