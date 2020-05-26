# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
N ?= 8

include ../fuzzer.mk

database: build/segbits_bramx.block_ram.db

build/segbits_bramx.block_ram.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_bramx.block_ram.rdb $(addsuffix /segdata_bram_[lr].txt,$(SPECIMENS))

build/segbits_bramx.block_ram.db: build/segbits_bramx.block_ram.rdb
	cp $^ $@
	${XRAY_MASKMERGE} build/mask_bramx.block_ram.db $(addsuffix /segdata_bram_[lr].txt,$(SPECIMENS))

pushdb:
	${XRAY_MERGEDB} bram_l.block_ram build/segbits_bramx.block_ram.db
	${XRAY_MERGEDB} bram_r.block_ram build/segbits_bramx.block_ram.db
	${XRAY_MERGEDB} mask_bram_l.block_ram build/mask_bramx.block_ram.db
	${XRAY_MERGEDB} mask_bram_r.block_ram build/mask_bramx.block_ram.db

.PHONY: database pushdb
