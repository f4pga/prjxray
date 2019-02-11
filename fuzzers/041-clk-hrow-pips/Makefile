N ?= 150

SPECIMENS_DEPS=build/cmt_regions.csv
include ../fuzzer.mk

database: build/segbits_clk_hrow.db

build/clk_hrow_bot_r.txt: clk_hrow_pip_list.tcl
	mkdir -p build
	cd build/ && ${XRAY_VIVADO} -mode batch -source ${FUZDIR}/clk_hrow_pip_list.tcl

build/cmt_regions.csv: output_cmt.tcl build/clk_hrow_bot_r.txt
	mkdir -p build
	cd build/ && ${XRAY_VIVADO} -mode batch -source ${FUZDIR}/output_cmt.tcl

build/segbits_clk_hrow.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_clk_hrow.rdb \
		$(addsuffix /segdata_clk_hrow_top_r.txt,$(SPECIMENS)) \
		$(addsuffix /segdata_clk_hrow_bot_r.txt,$(SPECIMENS))

build/segbits_clk_hrow.db: build/segbits_clk_hrow.rdb build/clk_hrow_bot_r.txt
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_clk_hrow.rdb \
		--seg-fn-out build/segbits_clk_hrow_rc.db
	python3 merge_clk_entries.py \
		build/segbits_clk_hrow_rc.db \
		build/clk_hrow_bot_r.txt \
		build/segbits_clk_hrow.db

	${XRAY_MASKMERGE} build/mask_clk_hrow.db \
		$(addsuffix /segdata_clk_hrow_top_r.txt,$(SPECIMENS)) \
		$(addsuffix /segdata_clk_hrow_bot_r.txt,$(SPECIMENS))

pushdb: database
	${XRAY_MERGEDB} clk_hrow_bot_r build/segbits_clk_hrow.db
	${XRAY_MERGEDB} clk_hrow_top_r build/segbits_clk_hrow.db
	${XRAY_MERGEDB} mask_clk_hrow_bot_r build/mask_clk_hrow.db
	${XRAY_MERGEDB} mask_clk_hrow_top_r build/mask_clk_hrow.db

.PHONY: database pushdb
