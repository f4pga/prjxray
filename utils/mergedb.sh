#!/bin/bash
set -ex
test $# = 2
test -e "$2"

tmp1=`mktemp -p .`
tmp2=`mktemp -p .`

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
	clbll_int_l)
		sed < "$2" > "$tmp1" -e 's/^INT\./CLBLL_INT_L./' ;;
	clbll_int_r)
		sed < "$2" > "$tmp1" -e 's/^INT\./CLBLL_INT_R./' ;;
	clblm_int_l)
		sed < "$2" > "$tmp1" -e 's/^INT\./CLBLM_INT_L./' ;;
	clblm_int_r)
		sed < "$2" > "$tmp1" -e 's/^INT\./CLBLM_INT_R./' ;;
	clbll_mask_l)
		sed < "$2" > "$tmp1" -e 's/^bit/CLBLL_MASK_L/' ;;
	clbll_mask_r)
		sed < "$2" > "$tmp1" -e 's/^bit/CLBLL_MASK_R/' ;;
	clblm_mask_l)
		sed < "$2" > "$tmp1" -e 's/^bit/CLBLM_MASK_L/' ;;
	clblm_mask_r)
		sed < "$2" > "$tmp1" -e 's/^bit/CLBLM_MASK_R/' ;;
	*)
		echo "Invalid mode: $1"
		rm -f "$tmp1" "$tmp2"
		exit 1
esac

db=../../database/$XRAY_DATABASE/seg_$1.segbits
touch "$db"
sort -u "$tmp1" "$db" | grep -v '<.*>' > "$tmp2"
mv "$tmp2" "$db"
rm -f "$tmp1"

