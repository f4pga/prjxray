# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
export FUZDIR=$(shell pwd)
PIP_TYPE?=clk_hrow
PIPLIST_TCL=$(FUZDIR)/clk_hrow_pip_list.tcl

TODO_RE=".*"

MAKETODO_FLAGS=--sides "bot_r,top_r" --pip-type ${PIP_TYPE} --seg-type clk_hrow --re $(TODO_RE) --balance-wire-re "^CLK_HROW_" --balance-wire-cnt "2"
N = 50

# These PIPs all appear to be either a 2 bit solutions.
SEGMATCH_FLAGS=-c 2
SPECIMENS_DEPS=build/dump.ok
A_PIPLIST=clk_hrow_bot_r.txt

include ../pip_loop.mk

database: build/segbits_clk_hrow_bot_r.rdb build/segbits_clk_hrow_top_r.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_clk_hrow_top_r.rdb \
		--seg-fn-out build/segbits_clk_hrow_top_r.db
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_clk_hrow_bot_r.rdb \
		--seg-fn-out build/segbits_clk_hrow_bot_r.db

	# Keep a copy to track iter progress
	cp build/segbits_clk_hrow_top_r.rdb build/$(ITER)/segbits_clk_hrow_top_r.rdb
	cp build/segbits_clk_hrow_bot_r.rdb build/$(ITER)/segbits_clk_hrow_bot_r.rdb

	${XRAY_MASKMERGE} build/mask_clk_hrow_top_r.db \
		$(shell find build -name segdata_clk_hrow_top_r.txt)
	${XRAY_MASKMERGE} build/mask_clk_hrow_bot_r.db \
		$(shell find build -name segdata_clk_hrow_bot_r.txt)

	# Clobber existing .db to eliminate potential conflicts
	rm -f build/database/${XRAY_DATABASE}/*
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db build/database/${XRAY_DATABASE}
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} clk_hrow_bot_r build/segbits_clk_hrow_bot_r.db
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} clk_hrow_top_r build/segbits_clk_hrow_top_r.db

ifeq (${XRAY_DATABASE}, zynq7)
build/dump.ok: output_cmt.tcl output_pss_clocks.tcl
	mkdir -p build
	cd build/ && ${XRAY_VIVADO} -mode batch -source ${FUZDIR}/output_cmt.tcl
	cd build/ && ${XRAY_VIVADO} -mode batch -source ${FUZDIR}/output_pss_clocks.tcl
	touch build/dump.ok
else
build/dump.ok: output_cmt.tcl
	mkdir -p build
	cd build/ && ${XRAY_VIVADO} -mode batch -source ${FUZDIR}/output_cmt.tcl
	touch build/dump.ok
endif

generate: $(SPECIMENS_OK)

build/segbits_clk_hrow_top_r.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} ${SEGMATCH_FLAGS} -o build/segbits_clk_hrow_top_r.rdb \
		$(shell find build -name segdata_clk_hrow_top_r.txt)

build/segbits_clk_hrow_bot_r.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} ${SEGMATCH_FLAGS} -o build/segbits_clk_hrow_bot_r.rdb \
		$(shell find build -name segdata_clk_hrow_bot_r.txt)

build/segbits_clk_hrow.db: build/segbits_clk_hrow_top_.rdb

pushdb: database
	${XRAY_MERGEDB} clk_hrow_bot_r build/segbits_clk_hrow_bot_r.db
	${XRAY_MERGEDB} clk_hrow_top_r build/segbits_clk_hrow_top_r.db
	${XRAY_MERGEDB} mask_clk_hrow_bot_r build/mask_clk_hrow_bot_r.db
	${XRAY_MERGEDB} mask_clk_hrow_top_r build/mask_clk_hrow_top_r.db

.PHONY: database pushdb generate
