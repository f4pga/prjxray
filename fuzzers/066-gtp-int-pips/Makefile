# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
export FUZDIR=$(shell pwd)
PIP_TYPE?=gtp_int_interface
SEG_TYPE?=gtp_int_interface
PIPLIST_TCL=$(FUZDIR)/gtp_int_interface_pip_list.tcl

BUILD_DIR = build
RUN_OK = run.ok

TODO_RE=".*"

MAKETODO_FLAGS=--pip-type ${PIP_TYPE} --seg-type $(SEG_TYPE) --re $(TODO_RE) --sides ""
N = 2

SEGMATCH_FLAGS=-c 1

A_PIPLIST=gtp_int_interface.txt

CHECK_ARGS= --zero-entries --timeout-iters 2

include ../pip_loop.mk

$(BUILD_DIR)/segbits_gtp_int_interface.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} ${SEGMATCH_FLAGS} -o $(BUILD_DIR)/segbits_gtp_int_interface.rdb \
		$(shell find $(BUILD_DIR) -name segdata_gtp_int_interface*.txt)

RDBS = $(BUILD_DIR)/segbits_gtp_int_interface.rdb

database: ${RDBS}
	${XRAY_DBFIXUP} --db-root $(BUILD_DIR) --zero-db bits.dbf \
		--seg-fn-in $(BUILD_DIR)/segbits_gtp_int_interface.rdb \
		--seg-fn-out $(BUILD_DIR)/segbits_gtp_int_interface.db

	# Keep a copy to track iter progress
	cp $(BUILD_DIR)/segbits_gtp_int_interface.rdb $(BUILD_DIR)/$(ITER)/segbits_gtp_int_interface.rdb
	cp $(BUILD_DIR)/segbits_gtp_int_interface.db $(BUILD_DIR)/$(ITER)/segbits_gtp_int_interface.db

	# Clobber existing .db to eliminate potential conflicts
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db $(BUILD_DIR)/database/${XRAY_DATABASE}
	XRAY_DATABASE_DIR=$(BUILD_DIR)/database ${XRAY_MERGEDB} gtp_int_interface_l $(BUILD_DIR)/segbits_gtp_int_interface.db
	XRAY_DATABASE_DIR=$(BUILD_DIR)/database ${XRAY_MERGEDB} gtp_int_interface_r $(BUILD_DIR)/segbits_gtp_int_interface.db
	XRAY_DATABASE_DIR=$(BUILD_DIR)/database ${XRAY_MERGEDB} gtp_int_interface $(BUILD_DIR)/segbits_gtp_int_interface.db

pushdb: database
	${XRAY_MERGEDB} gtp_int_interface_l $(BUILD_DIR)/segbits_gtp_int_interface.db
	${XRAY_MERGEDB} gtp_int_interface_r $(BUILD_DIR)/segbits_gtp_int_interface.db
	${XRAY_MERGEDB} gtp_int_interface $(BUILD_DIR)/segbits_gtp_int_interface.db

.PHONY: database pushdb run clean
