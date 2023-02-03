# Copyright (C) 2017-2023  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
N := 5
include ../fuzzer.mk

database: build/segbits_riob18.db

build/segbits_riob18.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -m 1 -M 1 -o build/segbits_riob18.rdb $$(find -name segdata_*.txt)

build/segbits_riob18.db: build/segbits_riob18.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_riob18.db $$(find -name segdata_*.txt)

pushdb:
	${XRAY_MERGEDB} rioi build/segbits_riob18.db
	${XRAY_MERGEDB} rioi_tbytesrc build/segbits_riob18.db
	${XRAY_MERGEDB} rioi_tbyteterm build/segbits_riob18.db
	${XRAY_MERGEDB} mask_rioi build/mask_riob18.db
	${XRAY_MERGEDB} mask_rioi_tbytesrc build/mask_riob18.db
	${XRAY_MERGEDB} mask_rioi_tbyteterm build/mask_riob18.db

.PHONY: database pushdb

