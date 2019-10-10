export FUZDIR=$(shell pwd)
PIP_TYPE?=cmt_top
PIPLIST_TCL=$(FUZDIR)/cmt_top_upper_t.tcl
TODO_RE=".*\.CMT_TOP_[LR]_UPPER_T_PLLE2_CLK_[^_]+_INT"

ifneq (${XRAY_DATABASE}, zynq7)
MAKETODO_FLAGS=--sides "r_upper_t,l_upper_t" --pip-type ${PIP_TYPE} --seg-type cmt_top --re $(TODO_RE)
else
MAKETODO_FLAGS=--sides "l_upper_t" --pip-type ${PIP_TYPE} --seg-type cmt_top --re $(TODO_RE)
endif
N = 100

A_PIPLIST=cmt_top_l_upper_t.txt

include ../pip_loop.mk

build/segbits_cmt_top_l_upper_t.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} ${SEGMATCH_FLAGS} -o build/segbits_cmt_top_l_upper_t.rdb \
		$(shell find build -name segdata_cmt_top_l_upper_t.txt)

RDBS = build/segbits_cmt_top_l_upper_t.rdb

ifneq (${XRAY_DATABASE}, zynq7)
# Target Zynq7 part has no CMT_TOP_R_UPPER_T
build/segbits_cmt_top_r_upper_t.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} ${SEGMATCH_FLAGS} -o build/segbits_cmt_top_r_upper_t.rdb \
		$(shell find build -name segdata_cmt_top_r_upper_t.txt)

RDBS += build/segbits_cmt_top_r_upper_t.rdb
endif

database: ${RDBS}
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_cmt_top_l_upper_t.rdb \
		--seg-fn-out build/segbits_cmt_top_l_upper_t.db

ifneq (${XRAY_DATABASE}, zynq7)
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_cmt_top_r_upper_t.rdb \
		--seg-fn-out build/segbits_cmt_top_r_upper_t.db
endif

	# Keep a copy to track iter progress
	cp build/segbits_cmt_top_l_upper_t.rdb build/$(ITER)/segbits_cmt_top_l_upper_t.rdb
	cp build/segbits_cmt_top_l_upper_t.db build/$(ITER)/segbits_cmt_top_l_upper_t.db
ifneq (${XRAY_DATABASE}, zynq7)
	cp build/segbits_cmt_top_r_upper_t.rdb build/$(ITER)/segbits_cmt_top_r_upper_t.rdb
	cp build/segbits_cmt_top_r_upper_t.db build/$(ITER)/segbits_cmt_top_r_upper_t.db
endif


	${XRAY_MASKMERGE} build/mask_cmt_top_l_upper_t.db \
		$(shell find build -name segdata_cmt_top_l_upper_t.txt)
ifneq (${XRAY_DATABASE}, zynq7)
	${XRAY_MASKMERGE} build/mask_cmt_top_r_upper_t.db \
		$(shell find build -name segdata_cmt_top_r_upper_t.txt)
endif

	# Clobber existing .db to eliminate potential conflicts
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db build/database/${XRAY_DATABASE}
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} cmt_top_l_upper_t build/segbits_cmt_top_l_upper_t.db
ifneq (${XRAY_DATABASE}, zynq7)
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} cmt_top_r_upper_t build/segbits_cmt_top_r_upper_t.db
endif

pushdb: database
	${XRAY_MERGEDB} cmt_top_l_upper_t build/segbits_cmt_top_l_upper_t.db
ifneq (${XRAY_DATABASE}, zynq7)
	${XRAY_MERGEDB} cmt_top_r_upper_t build/segbits_cmt_top_r_upper_t.db
endif

.PHONY: database pushdb
