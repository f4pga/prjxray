# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
N := 50
include ../fuzzer.mk

database: build/segbits_rioi.db

build/segbits_rioi.rdb2: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 20 -m 1 -M 1 -o build/segbits_rioi.rdb2 $$(find -name segdata_*.txt)

build/segbits_rioi.rdb: build/segbits_rioi.rdb2
	# Keep only solution for ISERDES related features.
	grep -e ".ISERDES." $^ >$@
	grep -e ".IDDR.IN_USE." $^ >>$@

build/segbits_rioi.db: build/segbits_rioi.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --groups tag_groups.txt --seg-fn-in $^ --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_rioi.db $$(find -name segdata_*.txt)

pushdb:
	${XRAY_MERGEDB} rioi build/segbits_rioi.db
	${XRAY_MERGEDB} rioi_tbytesrc build/segbits_rioi.db
	${XRAY_MERGEDB} rioi_tbyteterm build/segbits_rioi.db
	${XRAY_MERGEDB} mask_rioi build/mask_rioi.db
	${XRAY_MERGEDB} mask_rioi_tbytesrc build/mask_rioi.db
	${XRAY_MERGEDB} mask_rioi_tbyteterm build/mask_rioi.db

.PHONY: database pushdb

