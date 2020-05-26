#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

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

