# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
export FUZDIR=$(shell pwd)
PIP_TYPE?=gtp_common_mid_${XRAY_PART}
PIP_FILE?=gtp_common_mid
SEG_TYPE?=gtp_common_mid_left
PIPLIST_TCL=$(FUZDIR)/gtp_common_pip_list.tcl

BUILD_DIR = ${FUZDIR}/build_${XRAY_PART}
RUN_OK = run.${XRAY_PART}.ok

TODO_RE=".*"
EXCLUDE_RE=".*HCLK_GTP_CK_MUX.*"
PIP_DIR=${XRAY_FUZZERS_DIR}/piplist/build/$(PIP_TYPE)

MAKETODO_FLAGS=--pip-type ${PIP_FILE} --seg-type $(SEG_TYPE) --re $(TODO_RE) --sides "" --exclude-re $(EXCLUDE_RE) --pip-dir $(PIP_DIR)
N = 60

SEGMATCH_FLAGS=-c 2
SPECIMENS_DEPS=$(BUILD_DIR)/cmt_regions.csv
A_PIPLIST=gtp_common_mid.txt

CHECK_ARGS= --zero-entries --timeout-iters 5 --todo-dir $(BUILD_DIR)/todo

include ../pip_loop.mk

$(BUILD_DIR)/segbits_gtp_common.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} ${SEGMATCH_FLAGS} -o $(BUILD_DIR)/segbits_gtp_common.rdb \
		$(shell find $(BUILD_DIR) -name segdata_gtp_common*.txt)

RDBS = $(BUILD_DIR)/segbits_gtp_common.rdb

database: ${RDBS}
	${XRAY_DBFIXUP} --db-root $(BUILD_DIR) --zero-db bits.dbf \
		--seg-fn-in $(BUILD_DIR)/segbits_gtp_common.rdb \
		--seg-fn-out $(BUILD_DIR)/segbits_gtp_common.db

	# Keep a copy to track iter progress
	cp $(BUILD_DIR)/segbits_gtp_common.rdb $(BUILD_DIR)/$(ITER)/segbits_gtp_common.rdb
	cp $(BUILD_DIR)/segbits_gtp_common.db $(BUILD_DIR)/$(ITER)/segbits_gtp_common.db

	# Clobber existing .db to eliminate potential conflicts
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db $(BUILD_DIR)/database/${XRAY_DATABASE}
	XRAY_DATABASE_DIR=$(BUILD_DIR)/database ${XRAY_MERGEDB} gtp_common_mid_left $(BUILD_DIR)/segbits_gtp_common.db
	XRAY_DATABASE_DIR=$(BUILD_DIR)/database ${XRAY_MERGEDB} gtp_common_mid_right $(BUILD_DIR)/segbits_gtp_common.db

$(BUILD_DIR)/cmt_regions.csv: output_cmt.tcl
	mkdir -p $(BUILD_DIR)
	cd $(BUILD_DIR)/ && ${XRAY_VIVADO} -mode batch -source ${FUZDIR}/output_cmt.tcl

clean:
	rm -rf ${BUILD_DIR} ${RUN_OK}

pushdb: database
	${XRAY_MERGEDB} gtp_common_mid_left $(BUILD_DIR)/segbits_gtp_common.db
	${XRAY_MERGEDB} gtp_common_mid_right $(BUILD_DIR)/segbits_gtp_common.db

.PHONY: database pushdb run clean
