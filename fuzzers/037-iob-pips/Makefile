export FUZDIR=$(shell pwd)
PIP_TYPE?=ioi3
PIPLIST_TCL=$(FUZDIR)/ioi3_pip_list.tcl

TODO_RE="[LR]IOI3\.(IOI_([IO]LOGIC[01]_CLK(DIV|B)?)|(IOI_OCLK_[01]))\.IOI_LEAF_GCLK[0-9]"

MAKETODO_FLAGS=--pip-type ${PIP_TYPE} --seg-type $(PIP_TYPE) --re $(TODO_RE)
N = 40

SEGMATCH_FLAGS=-c 2 -m 15 -M 30
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


	${XRAY_MASKMERGE} build/mask_xioi3.db \
		$(shell find build -name segdata_ioi3_l.txt) \
		$(shell find build -name segdata_ioi3_r.txt)

	# Clobber existing .db to eliminate potential conflicts
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db build/database/${XRAY_DATABASE}
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} ioi3_l build/segbits_ioi3_x.db
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} ioi3_r build/segbits_ioi3_x.db

build/cmt_regions.csv: output_cmt.tcl
	mkdir -p build
	cd build/ && ${XRAY_VIVADO} -mode batch -source ${FUZDIR}/output_cmt.tcl

pushdb:
	${XRAY_MERGEDB} lioi3 build/segbits_ioi3_x.db
	${XRAY_MERGEDB} rioi3 build/segbits_ioi3_x.db

.PHONY: database pushdb
