export FUZDIR=$(shell pwd)
PIP_TYPE?=cmt_top
PIPLIST_TCL=$(FUZDIR)/cmt_top_upper_t.tcl
TODO_RE=".*"

MAKETODO_FLAGS=--sides "r_upper_t,l_upper_t" --pip-type ${PIP_TYPE} --seg-type cmt_top --re $(TODO_RE)
N = 50

A_PIPLIST=cmt_top_l_upper_t.txt

include ../pip_loop.mk

build/segbits_cmt_top_l_upper_t.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} ${SEGMATCH_FLAGS} -o build/segbits_cmt_top_l_upper_t.rdb \
		$(shell find build -name segdata_cmt_top_l_upper_t.txt)

build/segbits_cmt_top_r_upper_t.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} ${SEGMATCH_FLAGS} -o build/segbits_cmt_top_r_upper_t.rdb \
		$(shell find build -name segdata_cmt_top_r_upper_t.txt)

database: build/segbits_cmt_top_l_upper_t.rdb build/segbits_cmt_top_r_upper_t.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_cmt_top_l_upper_t.rdb \
		--seg-fn-out build/segbits_cmt_top_l_upper_t.db

	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_cmt_top_r_upper_t.rdb \
		--seg-fn-out build/segbits_cmt_top_r_upper_t.db

	# Keep a copy to track iter progress
	cp build/segbits_cmt_top_l_upper_t.rdb build/$(ITER)/segbits_cmt_top_l_upper_t.rdb
	cp build/segbits_cmt_top_l_upper_t.db build/$(ITER)/segbits_cmt_top_l_upper_t.db
	cp build/segbits_cmt_top_r_upper_t.rdb build/$(ITER)/segbits_cmt_top_r_upper_t.rdb
	cp build/segbits_cmt_top_r_upper_t.db build/$(ITER)/segbits_cmt_top_r_upper_t.db


	${XRAY_MASKMERGE} build/mask_cmt_top_l_upper_t.db \
		$(shell find build -name segdata_cmt_top_l_upper_t.txt)
	${XRAY_MASKMERGE} build/mask_cmt_top_r_upper_t.db \
		$(shell find build -name segdata_cmt_top_r_upper_t.txt)

	# Clobber existing .db to eliminate potential conflicts
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db build/database/${XRAY_DATABASE}
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} cmt_top_l_upper_t build/segbits_cmt_top_l_upper_t.db
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} cmt_top_r_upper_t build/segbits_cmt_top_r_upper_t.db

pushdb: database
	${XRAY_MERGEDB} cmt_top_l_upper_t build/segbits_cmt_top_l_upper_t.db
	${XRAY_MERGEDB} cmt_top_r_upper_t build/segbits_cmt_top_r_upper_t.db

.PHONY: database pushdb
