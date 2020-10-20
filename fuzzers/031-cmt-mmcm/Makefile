# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
N := 50
include ../fuzzer.mk

database: build/segbits_cmt_top_lower_b.db

build/segbits_cmt_top_lower_b.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 150 -o build/segbits_cmt_top_lower_b.rdb \
		$(shell find build -name "segdata_cmt_top_*_lower_b.txt")

build/segbits_cmt_top_lower_b.db: build/segbits_cmt_top_lower_b.rdb write_mmcm_reg.py
	python3 write_mmcm_reg.py \
		--seg_in build/segbits_cmt_top_lower_b.rdb \
		> build/segbits_cmt_top_lower_b.rdb2
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_cmt_top_lower_b.rdb2 \
		--seg-fn-out build/segbits_cmt_top_lower_b.db

pushdb: database
	${XRAY_MERGEDB} cmt_top_r_lower_b build/segbits_cmt_top_lower_b.db
	${XRAY_MERGEDB} cmt_top_l_lower_b build/segbits_cmt_top_lower_b.db

.PHONY: database pushdb

