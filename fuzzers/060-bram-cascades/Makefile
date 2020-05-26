# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
export FUZDIR=$(shell pwd)
PIP_TYPE?=bram_pips_int
PIPLIST_TCL=$(FUZDIR)/bram_pip_list.tcl
MAKETODO_FLAGS=--pip-type ${PIP_TYPE} --seg-type bram --re "BRAM_.\.BRAM_(?!LOGIC_OUTS).*"
N = 50

# These PIPs all appear to be either a 0 or 2 bit solution.
SEGMATCH_FLAGS=-m 20 -M 45 -c 2

include ../pip_loop.mk
#
# Specimens from current run must complete, but previous iterations may exist
database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} $(SEGMATCH_FLAGS) -o build/segbits_bram_x.rdb \
		$(shell find build -name segdata_bram_l.txt) \
		$(shell find build -name segdata_bram_r.txt)

	# Keep a copy to track iter progress
	# Also is pre-fixup, which drops and converts
	cp build/segbits_bram_x.rdb build/$(ITER)/segbits_bram_x.rdb
	${XRAY_DBFIXUP} --db-root build \
		--verbose \
		--zero-db bits.dbf \
		--seg-fn-in build/segbits_bram_x.rdb \
		--seg-fn-out build/segbits_bram_x.db

	python3 unmanagle_pips.py \
		--bram_x build/segbits_bram_x.db \
		--bram_l build/segbits_bram_l.db \
		--bram_r build/segbits_bram_r.db

	# Clobber existing .db to eliminate potential conflicts
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db build/database/${XRAY_DATABASE}
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} bram_l build/segbits_bram_l.db
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} bram_r build/segbits_bram_r.db

# Final pushdb to real repo
pushdb: database
	${XRAY_MERGEDB} bram_l build/segbits_bram_l.db
	${XRAY_MERGEDB} bram_r build/segbits_bram_r.db
