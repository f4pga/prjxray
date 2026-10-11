# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
N ?= 8

include ../fuzzer.mk

database: build/segbits_dsp_l.db build/segbits_dsp_r.db

SEGDATAS_L=$(addsuffix /segdata_dsp_l.txt,$(SPECIMENS))
SEGDATAS_R=$(addsuffix /segdata_dsp_r.txt,$(SPECIMENS))

build/segbits_dsp_l.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_dsp_l.rdb $(SEGDATAS_L)

build/segbits_dsp_l.db: build/segbits_dsp_l.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_dsp_l.db $(SEGDATAS_L)

build/segbits_dsp_r.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_dsp_r.rdb $(SEGDATAS_R)

build/segbits_dsp_r.db: build/segbits_dsp_r.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_dsp_r.db $(SEGDATAS_R)

pushdb: database
	${XRAY_MERGEDB} dsp_l build/segbits_dsp_l.db
	${XRAY_MERGEDB} dsp_r build/segbits_dsp_r.db
	${XRAY_MERGEDB} mask_dsp_l build/mask_dsp_l.db
	${XRAY_MERGEDB} mask_dsp_r build/mask_dsp_r.db

.PHONY: database pushdb

