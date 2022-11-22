# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
N := 30
include ../fuzzer.mk

database: build/segbits_xioi3.db

build/segbits_xioi3.rdb2: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 6 -o build/segbits_xioi3.rdb2 $$(find -name segdata_*)

build/segbits_xioi3.rdb: build/segbits_xioi3.rdb2
	# Filter out ISERDES features. Also filter DYN_CLK_INV_EN as they should
	# belong to ISEDRES and are solved by fuzzer 035b.
	grep -v ".ISERDES." $^ | grep -v "DYN_" >$@

build/segbits_xioi3.db: build/segbits_xioi3.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --groups tag_groups.txt --seg-fn-in $^ --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_xioi3.db $$(find -name segdata_*)

# fuzzers of the RIOI tiles give near identical results, so reuse these
build/segbits_rioi.db: build/segbits_xioi3.db
	sed 's/IOI3/IOI/g' < $< > $@

pushdb: build/segbits_rioi.db
	${XRAY_MERGEDB} lioi3 build/segbits_xioi3.db
	${XRAY_MERGEDB} lioi3_tbytesrc build/segbits_xioi3.db
	${XRAY_MERGEDB} lioi3_tbyteterm build/segbits_xioi3.db
	${XRAY_MERGEDB} rioi3 build/segbits_xioi3.db
	${XRAY_MERGEDB} rioi3_tbytesrc build/segbits_xioi3.db
	${XRAY_MERGEDB} rioi3_tbyteterm build/segbits_xioi3.db
	${XRAY_MERGEDB} mask_lioi3 build/mask_xioi3.db
	${XRAY_MERGEDB} mask_lioi3_tbytesrc build/mask_xioi3.db
	${XRAY_MERGEDB} mask_lioi3_tbyteterm build/mask_xioi3.db
	${XRAY_MERGEDB} mask_rioi3 build/mask_xioi3.db
	${XRAY_MERGEDB} mask_rioi3_tbytesrc build/mask_xioi3.db
	${XRAY_MERGEDB} mask_rioi3_tbyteterm build/mask_xioi3.db
ifeq ($(XRAY_DATABASE),kintex7)
	${XRAY_MERGEDB} rioi build/segbits_rioi.db
	${XRAY_MERGEDB} rioi_tbytesrc build/segbits_rioi.db
	${XRAY_MERGEDB} rioi_tbyteterm build/segbits_rioi.db
	${XRAY_MERGEDB} mask_rioi build/mask_xioi3.db
	${XRAY_MERGEDB} mask_rioi_tbytesrc build/mask_xioi3.db
	${XRAY_MERGEDB} mask_rioi_tbyteterm build/mask_xioi3.db
endif

.PHONY: database pushdb
