# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
export FUZDIR=$(shell pwd)
PIP_TYPE?=gtp_common
PIPLIST_TCL=$(FUZDIR)/gtp_common_pip_list.tcl


TODO_RE=".*"

MAKETODO_FLAGS=--pip-type ${PIP_TYPE} --seg-type $(PIP_TYPE) --re $(TODO_RE) --sides ""
N = 20

SEGMATCH_FLAGS=-c 2
SPECIMENS_DEPS=build/cmt_regions.csv
A_PIPLIST=gtp_common.txt

include ../pip_loop.mk

build/segbits_gtp_common.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} ${SEGMATCH_FLAGS} -o build/segbits_gtp_common.rdb \
		$(shell find build -name segdata_gtp_common*.txt)

RDBS = build/segbits_gtp_common.rdb

database: ${RDBS}
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_gtp_common.rdb \
		--seg-fn-out build/segbits_gtp_common.db

	# Keep a copy to track iter progress
	cp build/segbits_gtp_common.rdb build/$(ITER)/segbits_gtp_common.rdb
	cp build/segbits_gtp_common.db build/$(ITER)/segbits_gtp_common.db

	# Clobber existing .db to eliminate potential conflicts
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db build/database/${XRAY_DATABASE}
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} gtp_common build/segbits_gtp_common.db

build/cmt_regions.csv: output_cmt.tcl
	mkdir -p build
	cd build/ && ${XRAY_VIVADO} -mode batch -source ${FUZDIR}/output_cmt.tcl

pushdb: database
	${XRAY_MERGEDB} gtp_common_mid_left build/segbits_gtp_common.db
	${XRAY_MERGEDB} gtp_common_mid_right build/segbits_gtp_common.db

run:
	$(MAKE) clean
	+$(FUZDIR)/../int_loop.sh --check-args "--zero-entries --timeout-iters 10"
	touch run.${XRAY_PART}.ok

.PHONY: database pushdb run
