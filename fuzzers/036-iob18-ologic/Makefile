# Copyright (C) 2017-2022  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
N := 40
include ../fuzzer.mk

database: build/segbits_rioi.db

build/segbits_rioi.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 7 -o build/segbits_rioi.rdb $$(find -name segdata_*)

build/segbits_rioi.db: build/segbits_rioi.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_rioi.db $$(find -name segdata_*)

pushdb:
	${XRAY_MERGEDB} rioi build/segbits_rioi.db
	${XRAY_MERGEDB} rioi_tbytesrc build/segbits_rioi.db
	${XRAY_MERGEDB} rioi_tbyteterm build/segbits_rioi.db
	${XRAY_MERGEDB} mask_rioi build/mask_rioi.db
	${XRAY_MERGEDB} mask_rioi_tbytesrc build/mask_rioi.db
	${XRAY_MERGEDB} mask_rioi_tbyteterm build/mask_rioi.db

.PHONY: database pushdb

