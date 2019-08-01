export FUZDIR=$(shell pwd)
PIP_TYPE?=ioi3
PIPLIST_TCL=$(FUZDIR)/ioi3_pip_list.tcl

TODO_RE=".*"
EXCLUDE_RE=".*((PHASER)|(CLKDIVF)|(CLKDIVP)|(CLKDIVB)|(IOI_ILOGIC[01]_O)|(IOI_OLOGIC[01]_CLKB?\.)|(IOI_IMUX_RC)|(IOI_OLOGIC[01]_[OT]FB)).*"

MAKETODO_FLAGS=--pip-type ${PIP_TYPE} --seg-type $(PIP_TYPE) --re $(TODO_RE) --sides "xr,xl" --exclude-re $(EXCLUDE_RE)
N = 40

A_PIPLIST=lioi3.txt

SEGMATCH_FLAGS=-c 6 -m 20 -M 50
SPECIMENS_DEPS=build/cmt_regions.csv

include ../pip_loop.mk

build/segbits_ioi3_x.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} ${SEGMATCH_FLAGS} -o build/segbits_ioi3_x.rdb \
		$(shell find build -name segdata_lioi3*.txt) $(shell find build -name segdata_rioi3*.txt)

RDBS = build/segbits_ioi3_x.rdb

database: ${RDBS}
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_ioi3_x.rdb \
		--seg-fn-out build/segbits_ioi3_x.db

	# Keep a copy to track iter progress
	cp build/segbits_ioi3_x.rdb build/$(ITER)/segbits_ioi3_x.rdb
	cp build/segbits_ioi3_x.db build/$(ITER)/segbits_ioi3_x.db

	# Clobber existing .db to eliminate potential conflicts
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db build/database/${XRAY_DATABASE}
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} lioi3 build/segbits_ioi3_x.db
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} rioi3 build/segbits_ioi3_x.db

build/cmt_regions.csv: output_cmt.tcl
	mkdir -p build
	cd build/ && ${XRAY_VIVADO} -mode batch -source ${FUZDIR}/output_cmt.tcl

pushdb: database
	${XRAY_MERGEDB} lioi3 build/segbits_ioi3_x.db
	${XRAY_MERGEDB} rioi3 build/segbits_ioi3_x.db
	${XRAY_MERGEDB} lioi3_tbytesrc build/segbits_ioi3_x.db
	${XRAY_MERGEDB} rioi3_tbytesrc build/segbits_ioi3_x.db
	${XRAY_MERGEDB} lioi3_tbyteterm build/segbits_ioi3_x.db
	${XRAY_MERGEDB} rioi3_tbyteterm build/segbits_ioi3_x.db

.PHONY: database pushdb
