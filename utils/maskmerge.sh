#!/bin/bash

outfile="$1"
shift

touch "$outfile"
mv "$outfile" "$outfile.tmp"

for infile; do
	echo "Reading mask bits from $infile."
	grep ^bit "$infile" | sort -u >> "$outfile.tmp"
done

sort -u < "$outfile.tmp" > "$outfile"
rm -f "$outfile.tmp"

