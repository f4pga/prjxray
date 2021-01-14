# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
N ?= 20

include ../fuzzer.mk

database: build/segbits_gtp_common.db

build/segbits_gtp_common.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_gtp_common.rdb $(addsuffix /segdata_gtp_common.txt,$(SPECIMENS))

build/segbits_gtp_common.db: build/segbits_gtp_common.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_gtp_common.rdb \
		--seg-fn-out build/segbits_gtp_common.db
	${XRAY_MASKMERGE} build/mask_gtp_common.db $(addsuffix /segdata_gtp_common.txt,$(SPECIMENS))

pushdb:
	${XRAY_MERGEDB} gtp_common build/segbits_gtp_common.db
	${XRAY_MERGEDB} mask_gtp_common build/mask_gtp_common.db

.PHONY: database pushdb
