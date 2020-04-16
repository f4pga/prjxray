# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
export FUZDIR=$(shell pwd)
PIP_TYPE?=clk_bufg
PIPLIST_TCL=$(FUZDIR)/clk_bufg_pip_list.tcl
TODO_RE=".*\.CLK_BUFG_(BOT|TOP)_R_CK_MUXED[0-9]+"

MAKETODO_FLAGS=--sides "bot_r,top_r" --pip-type ${PIP_TYPE} --seg-type clk_bufg --re $(TODO_RE)
N = 50

# These PIPs all appear to be either a 1 bit solutions.
SEGMATCH_FLAGS=-c 1
SPECIMENS_DEPS=build/cmt_regions.csv
A_PIPLIST=clk_bufg_bot_r.txt

include ../pip_loop.mk

build/segbits_clk_bufg_top_r.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} ${SEGMATCH_FLAGS} -o build/segbits_clk_bufg_top_r.rdb \
		$(shell find build -name segdata_clk_bufg_top_r.txt)

build/segbits_clk_bufg_bot_r.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} ${SEGMATCH_FLAGS} -o build/segbits_clk_bufg_bot_r.rdb \
		$(shell find build -name segdata_clk_bufg_bot_r.txt)


database: build/segbits_clk_bufg_top_r.rdb build/segbits_clk_bufg_bot_r.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_clk_bufg_bot_r.rdb \
		--seg-fn-out build/segbits_clk_bufg_bot_r.db

	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_clk_bufg_top_r.rdb \
		--seg-fn-out build/segbits_clk_bufg_top_r.db

	# Keep a copy to track iter progress
	cp build/segbits_clk_bufg_top_r.rdb build/$(ITER)/segbits_clk_bufg_top_r.rdb
	cp build/segbits_clk_bufg_top_r.db build/$(ITER)/segbits_clk_bufg_top_r.db
	cp build/segbits_clk_bufg_bot_r.rdb build/$(ITER)/segbits_clk_bufg_bot_r.rdb
	cp build/segbits_clk_bufg_bot_r.db build/$(ITER)/segbits_clk_bufg_bot_r.db


	${XRAY_MASKMERGE} build/mask_clk_bufg_top_r.db \
		$(shell find build -name segdata_clk_bufg_top_r.txt)
	${XRAY_MASKMERGE} build/mask_clk_bufg_bot_r.db \
		$(shell find build -name segdata_clk_bufg_bot_r.txt)

	# Clobber existing .db to eliminate potential conflicts
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db build/database/${XRAY_DATABASE}
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} clk_bufg_top_r build/segbits_clk_bufg_top_r.db
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} clk_bufg_bot_r build/segbits_clk_bufg_bot_r.db

build/cmt_regions.csv: output_cmt.tcl
	mkdir -p build
	cd build/ && ${XRAY_VIVADO} -mode batch -source ${FUZDIR}/output_cmt.tcl

pushdb: database
	${XRAY_MERGEDB} clk_bufg_bot_r build/segbits_clk_bufg_bot_r.db
	${XRAY_MERGEDB} clk_bufg_top_r build/segbits_clk_bufg_top_r.db
	${XRAY_MERGEDB} mask_clk_bufg_bot_r build/mask_clk_bufg_bot_r.db
	${XRAY_MERGEDB} mask_clk_bufg_top_r build/mask_clk_bufg_top_r.db

.PHONY: database pushdb
