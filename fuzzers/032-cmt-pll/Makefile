# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
N := 50
include ../fuzzer.mk

database: build/segbits_cmt_top_upper_t.db

build/segbits_cmt_top_upper_t.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 150 -o build/segbits_cmt_top_upper_t.rdb \
		$(shell find build -name "segdata_cmt_top_*_upper_t.txt")

build/segbits_cmt_top_upper_t.db: build/segbits_cmt_top_upper_t.rdb write_pll_reg.py
	python3 write_pll_reg.py \
		--seg_in build/segbits_cmt_top_upper_t.rdb \
		> build/segbits_cmt_top_upper_t.rdb2
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_cmt_top_upper_t.rdb2 \
		--seg-fn-out build/segbits_cmt_top_upper_t.db

pushdb: database
	${XRAY_MERGEDB} cmt_top_r_upper_t build/segbits_cmt_top_upper_t.db
	${XRAY_MERGEDB} cmt_top_l_upper_t build/segbits_cmt_top_upper_t.db

.PHONY: database pushdb

