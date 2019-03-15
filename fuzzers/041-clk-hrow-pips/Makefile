export FUZDIR=$(shell pwd)
PIP_TYPE?=clk_hrow
PIPLIST_TCL=$(FUZDIR)/clk_hrow_pip_list.tcl

ifeq (${XRAY_PART}, xc7z010clg400-1)
# xc7z010clg400-1 is missing some side clock connections, so these bits cannot
# be documented.
# FIXME: Use EXCLUDE_RE rather than complicated include RE.
TODO_RE="[^\.]+\.CLK_HROW_CK_MUX_OUT_[LR][0-9]+\.CLK_HROW_.*[KR_][0-9]+"
TODO_EXCLUDE_RE="^CLK_HROW_BOT_R.*CASCIN[0-9]+$$"
else
TODO_RE=".*"
TODO_EXCLUDE_RE="^CLK_HROW_BOT_R.*CASCIN[0-9]+$$"
endif

MAKETODO_FLAGS=--sides "bot_r,top_r" --pip-type ${PIP_TYPE} --seg-type clk_hrow --re $(TODO_RE) --exclude-re $(TODO_EXCLUDE_RE)
N = 50

# These PIPs all appear to be either a 2 bit solutions.
SEGMATCH_FLAGS=-c 2
SPECIMENS_DEPS=build/cmt_regions.csv
A_PIPLIST=clk_hrow_bot_r.txt

include ../pip_loop.mk

database: build/segbits_clk_hrow_bot_r.rdb build/segbits_clk_hrow_top_r.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_clk_hrow_top_r.rdb \
		--seg-fn-out build/segbits_clk_hrow_top_r.db
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_clk_hrow_bot_r.rdb \
		--seg-fn-out build/segbits_clk_hrow_bot_r.db

	# Keep a copy to track iter progress
	cp build/segbits_clk_hrow_top_r.rdb build/$(ITER)/segbits_clk_hrow_top_r.rdb
	cp build/segbits_clk_hrow_bot_r.rdb build/$(ITER)/segbits_clk_hrow_bot_r.rdb

	${XRAY_MASKMERGE} build/mask_clk_hrow_top_r.db \
		$(shell find build -name segdata_clk_hrow_top_r.txt)
	${XRAY_MASKMERGE} build/mask_clk_hrow_bot_r.db \
		$(shell find build -name segdata_clk_hrow_bot_r.txt)

	# Clobber existing .db to eliminate potential conflicts
	rm -f build/database/${XRAY_DATABASE}/*
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db build/database/${XRAY_DATABASE}
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} clk_hrow_bot_r build/segbits_clk_hrow_bot_r.db
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} clk_hrow_top_r build/segbits_clk_hrow_top_r.db

build/cmt_regions.csv: output_cmt.tcl
	mkdir -p build
	cd build/ && ${XRAY_VIVADO} -mode batch -source ${FUZDIR}/output_cmt.tcl

generate: $(SPECIMENS_OK)

build/segbits_clk_hrow_top_r.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} ${SEGMATCH_FLAGS} -o build/segbits_clk_hrow_top_r.rdb \
		$(shell find build -name segdata_clk_hrow_top_r.txt)

build/segbits_clk_hrow_bot_r.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} ${SEGMATCH_FLAGS} -o build/segbits_clk_hrow_bot_r.rdb \
		$(shell find build -name segdata_clk_hrow_bot_r.txt)

build/segbits_clk_hrow.db: build/segbits_clk_hrow_top_.rdb

pushdb: database
	${XRAY_MERGEDB} clk_hrow_bot_r build/segbits_clk_hrow_bot_r.db
	${XRAY_MERGEDB} clk_hrow_top_r build/segbits_clk_hrow_top_r.db
	${XRAY_MERGEDB} mask_clk_hrow_bot_r build/mask_clk_hrow_bot_r.db
	${XRAY_MERGEDB} mask_clk_hrow_top_r build/mask_clk_hrow_top_r.db

.PHONY: database pushdb generate
