N ?= 50

include ../fuzzer.mk

database: build/segbits_clk_bufg.db

build/segbits_clk_bufg.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_clk_bufg.rdb $(addsuffix /segdata_clk_bufg_top_r.txt,$(SPECIMENS)) $(addsuffix /segdata_clk_bufg_bot_r.txt,$(SPECIMENS))

build/segbits_clk_bufg.db: build/segbits_clk_bufg.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_clk_bufg.rdb \
		--seg-fn-out build/segbits_clk_bufg.db
	${XRAY_MASKMERGE} build/mask_clk_bufg.db $(addsuffix /segdata_clk_bufg_top_r.txt,$(SPECIMENS)) $(addsuffix /segdata_clk_bufg_bot_r.txt,$(SPECIMENS))

pushdb: database
	${XRAY_MERGEDB} clk_bufg_bot_r build/segbits_clk_bufg.db
	${XRAY_MERGEDB} clk_bufg_top_r build/segbits_clk_bufg.db
	${XRAY_MERGEDB} mask_clk_bufg_bot_r build/mask_clk_bufg.db
	${XRAY_MERGEDB} mask_clk_bufg_top_r build/mask_clk_bufg.db

.PHONY: database pushdb
