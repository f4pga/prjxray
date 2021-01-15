# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
N ?= 40

include ../fuzzer.mk

database: build/segbits_pcie_bot.db

build/segbits_pcie_bot.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_pcie_bot.rdb $(addsuffix /segdata_pcie_bot.txt,$(SPECIMENS))

build/segbits_pcie_bot.db: build/segbits_pcie_bot.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_pcie_bot.rdb \
		--seg-fn-out build/segbits_pcie_bot.db
	${XRAY_MASKMERGE} build/mask_pcie_bot.db $(addsuffix /segdata_pcie_bot.txt,$(SPECIMENS))

pushdb:
	${XRAY_MERGEDB} pcie_bot build/segbits_pcie_bot.db
	${XRAY_MERGEDB} mask_pcie_bot build/mask_pcie_bot.db

.PHONY: database pushdb
