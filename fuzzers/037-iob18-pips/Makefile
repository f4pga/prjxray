# Copyright (C) 2017-2022  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
export FUZDIR=$(shell pwd)
PIP_TYPE?=ioi
PIPLIST_TCL=$(FUZDIR)/ioi_pip_list.tcl

TODO_RE=".*"
EXCLUDE_RE=".*((PHASER)|(CLKDIVF)|(CLKDIVP)|(CLKDIVB)|(IOI_ILOGIC[01]_O)|(IOI_OLOGIC[01]_CLKB?\.)|(IOI_IMUX_RC)|(IOI_OLOGIC[01]_[OT]FB)|(OCLKM.*IMUX31)|IOI_ODELAY[01]_CLKIN.IOI_OCLK_[01]|RIOI_O[01].RIOI_ODELAY[01]_DATAOUT|RIOI_O[01].RIOI_OLOGIC[01]_OQ).*"

MAKETODO_FLAGS=--pip-type ${PIP_TYPE} --seg-type $(PIP_TYPE) --re $(TODO_RE) --sides "xr" --exclude-re $(EXCLUDE_RE)
N = 120

SPECIMENS_DEPS=build/cmt_regions.csv

include ../pip_loop.mk

SIX_BIT_PIPS="OLOGIC[01]_CLKDIV"

build/segbits_ioi_x.rdb: $(SPECIMENS_OK)
	# Most pips are 3 bits, force a 3 bit solution
	${XRAY_SEGMATCH} -c 3 -m 20 -M 50 -o build/segbits_ioi_x_match_3.rdb \
		$(shell find build -name segdata_rioi*.txt)
	# Some are 6 bit solutions, solve for 6 bits and merge respectively
	${XRAY_SEGMATCH} -c 6 -m 20 -M 50 -o build/segbits_ioi_x_match_6.rdb \
		$(shell find build -name segdata_rioi*.txt)
	grep -v ${SIX_BIT_PIPS} build/segbits_ioi_x_match_3.rdb  > build/segbits_ioi_x.rdb
	grep    ${SIX_BIT_PIPS} build/segbits_ioi_x_match_6.rdb >> build/segbits_ioi_x.rdb

RDBS = build/segbits_ioi_x.rdb

database: ${RDBS}
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_ioi_x.rdb \
		--seg-fn-out build/segbits_ioi_x.db

	# Keep a copy to track iter progress
	cp build/segbits_ioi_x.rdb build/$(ITER)/segbits_ioi_x.rdb
	cp build/segbits_ioi_x.db build/$(ITER)/segbits_ioi_x.db

	# Clobber existing .db to eliminate potential conflicts
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db build/database/${XRAY_DATABASE}
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} rioi build/segbits_ioi_x.db

build/cmt_regions.csv: output_cmt.tcl
	mkdir -p build
	cd build/ && ${XRAY_VIVADO} -mode batch -source ${FUZDIR}/output_cmt.tcl

pushdb: database
	${XRAY_MERGEDB} rioi build/segbits_ioi_x.db
	${XRAY_MERGEDB} rioi_tbytesrc build/segbits_ioi_x.db
	${XRAY_MERGEDB} rioi_tbyteterm build/segbits_ioi_x.db

.PHONY: database pushdb
