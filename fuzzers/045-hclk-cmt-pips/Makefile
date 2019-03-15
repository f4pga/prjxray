export FUZDIR=$(shell pwd)
PIP_TYPE?=hclk_cmt
PIPLIST_TCL=$(FUZDIR)/hclk_cmt_pip_list.tcl
TODO_RE=".*"
# Skipped pips:
# - LEAF wires are disconnected
# - FREQ_REF is only used by interconnect clocks, so low likelyhood of usage.
#   A BUFR can be used to clock divide if needed
# - PHSR PIPs are connected to PHASER sites, which are undocumented, so avoid
#   for now.
EXCLUDE_RE="(^.*LEAF)|(HCLK_CMT_L\.[^.]+\.HCLK_CMT_MUX_CLK_[0-9]+)|(HCLK_CMT\.[^.]+\.HCLK_CMT_CK_IN[0-9]+)|(^.*BUFMR)|(^.*FREQ_REF)|(^.*PHSR)|(^.*CLK_PLL7)|(^.*CLK_MMCM13)"

MAKETODO_FLAGS=--sides ",l" --pip-type ${PIP_TYPE} --seg-type ${PIP_TYPE} --re $(TODO_RE) --exclude-re $(EXCLUDE_RE)
N = 50

# These PIPs all appear to be either a 1 bit solutions.
SEGMATCH_FLAGS=-c 2
SPECIMENS_DEPS=build/cmt_regions.csv
A_PIPLIST=hclk_cmt.txt

include ../pip_loop.mk

build/segbits_hclk_cmt.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} ${SEGMATCH_FLAGS} -o build/segbits_hclk_cmt.rdb \
		$(shell find build -name segdata_hclk_cmt.txt)

build/segbits_hclk_cmt_l.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} ${SEGMATCH_FLAGS} -o build/segbits_hclk_cmt_l.rdb \
		$(shell find build -name segdata_hclk_cmt_l.txt)

database: build/segbits_hclk_cmt.rdb build/segbits_hclk_cmt_l.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_hclk_cmt.rdb \
		--seg-fn-out build/segbits_hclk_cmt.db

	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_hclk_cmt_l.rdb \
		--seg-fn-out build/segbits_hclk_cmt_l.db

	# Keep a copy to track iter progress
	cp build/segbits_hclk_cmt.rdb build/$(ITER)/segbits_hclk_cmt.rdb
	cp build/segbits_hclk_cmt_l.rdb build/$(ITER)/segbits_hclk_cmt_l.rdb


	${XRAY_MASKMERGE} build/mask_hclk_cmt.db \
		$(shell find build -name segdata_hclk_cmt.txt)
	${XRAY_MASKMERGE} build/mask_hclk_cmt_l.db \
		$(shell find build -name segdata_hclk_cmt_l.txt)

	# Clobber existing .db to eliminate potential conflicts
	cp ${XRAY_DATABASE_DIR}/${XRAY_DATABASE}/segbits*.db build/database/${XRAY_DATABASE}
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} hclk_cmt build/segbits_hclk_cmt.db
	XRAY_DATABASE_DIR=${FUZDIR}/build/database ${XRAY_MERGEDB} hclk_cmt_l build/segbits_hclk_cmt_l.db

build/cmt_regions.csv: output_cmt.tcl
	mkdir -p build
	cd build/ && ${XRAY_VIVADO} -mode batch -source ${FUZDIR}/output_cmt.tcl

pushdb: database
	${XRAY_MERGEDB} hclk_cmt build/segbits_hclk_cmt.db
	${XRAY_MERGEDB} hclk_cmt_l build/segbits_hclk_cmt_l.db
	${XRAY_MERGEDB} mask_hclk_cmt build/mask_hclk_cmt.db
	${XRAY_MERGEDB} mask_hclk_cmt_l build/mask_hclk_cmt_l.db

.PHONY: database pushdb
