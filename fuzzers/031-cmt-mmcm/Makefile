# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
# read/write width is relatively slow to resolve
# Even slower with multi bit masks...
N := 14
include ../fuzzer.mk

SEGDATAS=$(addsuffix /segdata_cmt_top_r_lower_b.txt,$(SPECIMENS))

database: build/segbits_cmt_top_r_lower_b.db

build/segbits_cmt_top_r_lower_b.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_cmt_top_r_lower_b.rdb $(SEGDATAS)

build/segbits_cmt_top_r_lower_b.db: build/segbits_cmt_top_r_lower_b.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_cmt_top_r_lower_b.db $(SEGDATAS)

pushdb:
	${XRAY_MERGEDB} cmt_top_r_lower_b build/segbits_cmt_top_r_lower_b.db
	${XRAY_MERGEDB} mask_cmt_top_r_lower_b build/mask_cmt_top_r_lower_b.db

.PHONY: database pushdb

