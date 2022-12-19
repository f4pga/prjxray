# Copyright (C) 2017-2022  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
N := 40
SPECIMENS_DEPS := build/iobanks.txt
include ../fuzzer.mk

database: build/segbits_riob18.db build/segbits_hclk_ioi.db

build/iobanks.txt: write_io_banks.tcl
	mkdir -p build
	cd build/ && ${XRAY_VIVADO} -mode batch -source ../write_io_banks.tcl

build/segbits_riob18.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 23 -o build/segbits_riob18.rdb $$(find -name segdata_riob18.txt)

build/segbits_riob18.db: build/segbits_riob18.rdb process_rdb.py bits.dbf
#   delete the Y1 LVDS tags because they are empty anyway and are missing the DRIVE tag which upsets process_rdb.py
	sed '/IOB18.IOB_Y1.LVDS/d' -i build/segbits_riob18.rdb
	python3 process_rdb.py build/segbits_riob18.rdb > build/segbits_riob18_processed.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --groups tag_groups.txt --seg-fn-in build/segbits_riob18_processed.rdb --seg-fn-out $@
	# TODO: This is a hack. See https://github.com/f4pga/prjxray/issues/2073
	echo 'RIOB18.IOB_Y0.SSTL12_SSTL135_SSTL15.IN !38_126 39_127' >> $@
	sort -o $@ $@
	${XRAY_MASKMERGE} build/mask_riob18.db $$(find -name segdata_riob18.txt)

build/segbits_hclk_ioi.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 10 -o build/segbits_hclk_ioi.rdb $$(find -name segdata_hclk_ioi.txt)

build/segbits_hclk_ioi.db: build/segbits_hclk_ioi.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db hclk_bits.dbf --seg-fn-in build/segbits_hclk_ioi.rdb --seg-fn-out $@

pushdb:
	${XRAY_MERGEDB} riob18 build/segbits_riob18.db
	${XRAY_MERGEDB} mask_riob18 build/mask_riob18.db

	${XRAY_MERGEDB} hclk_ioi build/segbits_hclk_ioi.db

.PHONY: database pushdb

