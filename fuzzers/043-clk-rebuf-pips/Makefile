# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
N ?= 50

include ../fuzzer.mk

database: build/segbits_clk_bufg_rebuf.db

build/segbits_clk_bufg_rebuf.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 1 -o build/segbits_clk_bufg_rebuf.rdb \
		$(addsuffix /segdata_clk_bufg_rebuf.txt,$(SPECIMENS))

build/segbits_clk_bufg_rebuf.db: build/segbits_clk_bufg_rebuf.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_clk_bufg_rebuf.rdb \
		--seg-fn-out build/segbits_clk_bufg_rebuf.db
	${XRAY_MASKMERGE} build/mask_clk_bufg_rebuf.db \
		$(addsuffix /segdata_clk_bufg_rebuf.txt,$(SPECIMENS))

pushdb: database
	${XRAY_MERGEDB} clk_bufg_rebuf build/segbits_clk_bufg_rebuf.db
	${XRAY_MERGEDB} mask_clk_bufg_rebuf build/mask_clk_bufg_rebuf.db

.PHONY: database pushdb
