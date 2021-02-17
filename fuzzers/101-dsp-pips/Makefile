# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
export FUZDIR=$(shell pwd)
PIP_TYPE?=dsp
PIPLIST_TCL=$(FUZDIR)/dsp_pip_list.tcl

BUILD_DIR = build
RUN_OK = run.ok

TODO_RE=".*"

MAKETODO_FLAGS=--pip-type ${PIP_TYPE} --seg-type $(PIP_TYPE) --re $(TODO_RE) --sides "l,r"
N = 1

SEGMATCH_FLAGS=-c 1

A_PIPLIST=dsp_l.txt

CHECK_ARGS= --zero-entries --timeout-iters 2

include ../pip_loop.mk

$(BUILD_DIR)/segbits_dsp_l.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} ${SEGMATCH_FLAGS} -o $(BUILD_DIR)/segbits_dsp_l.rdb \
		$(shell find $(BUILD_DIR) -name segdata_dsp_l.txt)

$(BUILD_DIR)/segbits_dsp_r.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} ${SEGMATCH_FLAGS} -o $(BUILD_DIR)/segbits_dsp_r.rdb \
		$(shell find $(BUILD_DIR) -name segdata_dsp_r.txt)

RDBS = $(BUILD_DIR)/segbits_dsp_l.rdb $(BUILD_DIR)/segbits_dsp_r.rdb

database: ${RDBS}
	${XRAY_DBFIXUP} --db-root $(BUILD_DIR) --zero-db bits.dbf \
		--seg-fn-in $(BUILD_DIR)/segbits_dsp_l.rdb \
		--seg-fn-out $(BUILD_DIR)/segbits_dsp_l.db
	${XRAY_DBFIXUP} --db-root $(BUILD_DIR) --zero-db bits.dbf \
		--seg-fn-in $(BUILD_DIR)/segbits_dsp_r.rdb \
		--seg-fn-out $(BUILD_DIR)/segbits_dsp_r.db

	# Keep a copy to track iter progress
	cp $(BUILD_DIR)/segbits_dsp_l.rdb $(BUILD_DIR)/$(ITER)/segbits_dsp_l.rdb
	cp $(BUILD_DIR)/segbits_dsp_l.db $(BUILD_DIR)/$(ITER)/segbits_dsp_l.db
	cp $(BUILD_DIR)/segbits_dsp_r.rdb $(BUILD_DIR)/$(ITER)/segbits_dsp_r.rdb
	cp $(BUILD_DIR)/segbits_dsp_r.db $(BUILD_DIR)/$(ITER)/segbits_dsp_r.db

	# Clobber existing .db to eliminate potential conflicts
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db $(BUILD_DIR)/database/${XRAY_DATABASE}
	XRAY_DATABASE_DIR=$(BUILD_DIR)/database ${XRAY_MERGEDB} dsp_l $(BUILD_DIR)/segbits_dsp_l.db
	XRAY_DATABASE_DIR=$(BUILD_DIR)/database ${XRAY_MERGEDB} dsp_r $(BUILD_DIR)/segbits_dsp_r.db

pushdb: database
	${XRAY_MERGEDB} dsp_l $(BUILD_DIR)/segbits_dsp_l.db
	${XRAY_MERGEDB} dsp_r $(BUILD_DIR)/segbits_dsp_r.db

.PHONY: database pushdb run clean
