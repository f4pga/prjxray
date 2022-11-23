# Copyright (C) 2017-2022  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
export FUZDIR=$(shell pwd)
PIP_TYPE?=hclk_ioi
PIPLIST_TCL=$(FUZDIR)/hclk_ioi_pip_list.tcl
TODO_RE=".*"
# FIXME Modify fuzzer to solve PIPs that drive the BUFIO and BUFR from ILOGIC clock or through the IOI tile.
EXCLUDE_RE=".*\.HCLK_IOI_((I2IOCLK)|(IDELAYCTRL))"

MAKETODO_FLAGS= --sides "" --pip-type ${PIP_TYPE} --seg-type ${PIP_TYPE} --re $(TODO_RE) --exclude-re $(EXCLUDE_RE)
N = 499

SEGMATCH_FLAGS=-c 4 -m 4 -M 4
SPECIMENS_DEPS=build/cmt_regions.csv
A_PIPLIST=hclk_ioi.txt

include ../pip_loop.mk

build/segbits_hclk_ioi.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} ${SEGMATCH_FLAGS} -o build/segbits_hclk_ioi.rdb \
		$(shell find build -name segdata_hclk_ioi.txt)

build/segbits_hclk_ioi.db: build/segbits_hclk_ioi.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_hclk_ioi.rdb \
		--seg-fn-out build/segbits_hclk_ioi.db

	# Keep a copy to track iter progress
	cp build/segbits_hclk_ioi.rdb build/$(ITER)/segbits_hclk_ioi.rdb


	${XRAY_MASKMERGE} build/mask_hclk_ioi.db \
		$(shell find build -name segdata_hclk_ioi.txt)

database: build/segbits_hclk_ioi.db
	# Clobber existing .db to eliminate potential conflicts
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db build/database/${XRAY_DATABASE}
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} hclk_ioi build/segbits_hclk_ioi.db

build/cmt_regions.csv: output_cmt.tcl
	mkdir -p build
	cd build/ && ${XRAY_VIVADO} -mode batch -source ${FUZDIR}/output_cmt.tcl

pushdb: database
	${XRAY_MERGEDB} hclk_ioi build/segbits_hclk_ioi.db
	${XRAY_MERGEDB} mask_hclk_ioi build/mask_hclk_ioi.db

.PHONY: database pushdb
