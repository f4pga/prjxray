#!/bin/bash

set -ex
test $# = 2
test -e "$2"

tmp1=`mktemp -p .`
tmp2=`mktemp -p .`

db=$XRAY_DATABASE_DIR/$XRAY_DATABASE/segbits_$1.db

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

	int_l)
		sed < "$2" > "$tmp1" -e 's/^INT\./INT_L./' ;;
	int_r)
		sed < "$2" > "$tmp1" -e 's/^INT\./INT_R./' ;;

	hclk_l)
		sed < "$2" > "$tmp1" -e 's/^HCLK\./HCLK_L./' ;;
	hclk_r)
		sed < "$2" > "$tmp1" -e 's/^HCLK\./HCLK_R./' ;;

	mask_*)
		db=$XRAY_DATABASE_DIR/$XRAY_DATABASE/$1.db
		cp "$2" "$tmp1" ;;

	*)
		echo "Invalid mode: $1"
		rm -f "$tmp1" "$tmp2"
		exit 1
esac

touch "$db"
sort -u "$tmp1" "$db" | grep -v '<.*>' > "$tmp2" || true
mv "$tmp2" "$db"
rm -f "$tmp1"

