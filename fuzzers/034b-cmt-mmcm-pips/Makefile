# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
export FUZDIR=$(shell pwd)
PIP_TYPE?=cmt_top_lower
PIPLIST_TCL=$(FUZDIR)/cmt_top_lower_b.tcl
TODO_RE=".*CMT_LR_LOWER_B_MMCM_CLK(IN1|IN2|FBIN)\.CMT_[LR]"

MAKETODO_FLAGS=--sides "r_lower_b,l_lower_b" --pip-dir ${FUZDIR}/../piplist/build/cmt_top_lower --pip-type cmt_top --seg-type cmt_top --re $(TODO_RE)

N = 200
SEGMATCH_FLAGS=-m 10 -M 20 -c 300

A_PIPLIST=cmt_top_l_lower_b.txt

include ../pip_loop.mk

build/segbits_cmt_top_l_lower_b.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} ${SEGMATCH_FLAGS} -o build/segbits_cmt_top_lr_lower_b.rdb \
		$(shell find build -name segdata_cmt_top_l_lower_b.txt) \
		$(shell find build -name segdata_cmt_top_r_lower_b.txt)
	sed < build/segbits_cmt_top_lr_lower_b.rdb > build/segbits_cmt_top_l_lower_b.rdb -e 's/CMT_LRMAP_LOWER_B/CMT_L_LOWER_B/'
	sed < build/segbits_cmt_top_lr_lower_b.rdb > build/segbits_cmt_top_r_lower_b.rdb -e 's/CMT_LRMAP_LOWER_B/CMT_R_LOWER_B/'

RDBS = build/segbits_cmt_top_l_lower_b.rdb

database: ${RDBS}
	python3 ${FUZDIR}/fixup_and_group.py -g tag_groups.txt \
		-i build/segbits_cmt_top_l_lower_b.rdb \
		-o build/segbits_cmt_top_l_lower_b.db

	python3 ${FUZDIR}/fixup_and_group.py -g tag_groups.txt \
		-i build/segbits_cmt_top_r_lower_b.rdb \
		-o build/segbits_cmt_top_r_lower_b.db

	# Keep a copy to track iter progress
	cp build/segbits_cmt_top_l_lower_b.rdb build/$(ITER)/segbits_cmt_top_l_lower_b.rdb
	cp build/segbits_cmt_top_l_lower_b.db build/$(ITER)/segbits_cmt_top_l_lower_b.db
	cp build/segbits_cmt_top_r_lower_b.rdb build/$(ITER)/segbits_cmt_top_r_lower_b.rdb
	cp build/segbits_cmt_top_r_lower_b.db build/$(ITER)/segbits_cmt_top_r_lower_b.db

	# Clobber existing .db to eliminate potential conflicts
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db build/database/${XRAY_DATABASE}
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} cmt_top_l_lower_b build/segbits_cmt_top_l_lower_b.db
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} cmt_top_r_lower_b build/segbits_cmt_top_r_lower_b.db

pushdb: database
	${XRAY_MERGEDB} cmt_top_l_lower_b build/segbits_cmt_top_l_lower_b.db
	${XRAY_MERGEDB} cmt_top_r_lower_b build/segbits_cmt_top_r_lower_b.db

.PHONY: database pushdb
