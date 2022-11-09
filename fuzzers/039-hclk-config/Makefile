# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
N ?= 50

include ../fuzzer.mk

ifeq ($(XRAY_DATABASE),kintex7)
database: build/segbits_hclk_ioi.db
else
database: build/segbits_hclk_ioi3.db
endif

build/segbits_hclk_ioi3.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 5 -o build/segbits_hclk_ioi3.rdb \
		$(addsuffix /segdata_hclk_ioi3.txt,$(SPECIMENS))

build/segbits_hclk_ioi3.db: build/segbits_hclk_ioi3.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_hclk_ioi3.rdb \
		--seg-fn-out build/segbits_hclk_ioi3.db
	${XRAY_MASKMERGE} build/mask_hclk_ioi3.db \
		$(addsuffix /segdata_hclk_ioi3.txt,$(SPECIMENS))

# The fuzzer results for the high performance banks
# are identical, so just copy those
ifeq ($(XRAY_DATABASE),kintex7)
build/segbits_hclk_ioi.db: build/segbits_hclk_ioi3.db
	sed -e 's/HCLK_IOI3/HCLK_IOI/g' $< > $@
	cp build/mask_hclk_ioi3.db build/mask_hclk_ioi.db
endif

pushdb: database
	${XRAY_MERGEDB} hclk_ioi3 build/segbits_hclk_ioi3.db
	${XRAY_MERGEDB} mask_hclk_ioi3 build/mask_hclk_ioi3.db
ifeq ($(XRAY_DATABASE),kintex7)
	${XRAY_MERGEDB} hclk_ioi build/segbits_hclk_ioi.db
	${XRAY_MERGEDB} mask_hclk_ioi build/mask_hclk_ioi.db
endif

.PHONY: database pushdb
