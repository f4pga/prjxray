FUZDIR=$(shell pwd)
BUILD_DIR=$(FUZDIR)/build
TILEGRID_TDB_DEPENDENCIES=
TILEGRID_TDB_DEPENDENCIES += iob/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += iob_int/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += ioi/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += monitor/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += bram/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += bram_block/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += bram_int/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += clb/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += clb_int/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += cfg/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += dsp/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += fifo_int/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += cfg_int/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += monitor_int/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += clk_hrow/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += clk_bufg/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += hclk_cmt/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += pll/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += hclk_ioi/build/segbits_tilegrid.tdb
GENERATE_FULL_ARGS=

ifeq (${XRAY_DATABASE}, zynq7)
# Zynq7 only
TILEGRID_TDB_DEPENDENCIES += ps7_int/build/segbits_tilegrid.tdb
else
# Artix7/Kintex7 only
TILEGRID_TDB_DEPENDENCIES += mmcm/build/segbits_tilegrid.tdb
endif

ifeq (${XRAY_DATABASE}, kintex7)
TILEGRID_TDB_DEPENDENCIES += orphan_int_column/build/segbits_tilegrid.tdb
else
# Disable DSP INT fuzzer on kintex7.  It doesn't work, and isn't required.
TILEGRID_TDB_DEPENDENCIES += dsp_int/build/segbits_tilegrid.tdb
endif

database: build/tilegrid.json

pushdb: build/tilegrid.json
	cp build/tilegrid.json ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/tilegrid.json

build/tiles/tiles.txt:
	bash generate.sh build/tiles tiles

build/basicdb/tilegrid.json: generate.py build/tiles/tiles.txt
	mkdir -p build/basicdb
	cd build && python3 ${FUZDIR}/generate.py \
		--tiles $(FUZDIR)/build/tiles/tiles.txt \
		--out ${BUILD_DIR}/basicdb/tilegrid.json

clb/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd clb && $(MAKE)

clb_int/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd clb_int && $(MAKE)

cfg/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd cfg && $(MAKE)

iob/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd iob && $(MAKE)

iob_int/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd iob_int && $(MAKE)

ioi/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd ioi && $(MAKE)

mmcm/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd mmcm && $(MAKE)

pll/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd pll && $(MAKE)

ps7_int/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd ps7_int && $(MAKE)

monitor/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd monitor && $(MAKE)

monitor_int/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd monitor_int && $(MAKE)

bram/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd bram && $(MAKE)

bram_block/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd bram_block && $(MAKE)

bram_int/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd bram_int && $(MAKE)

dsp/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd dsp && $(MAKE)

dsp_int/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd dsp_int && $(MAKE)

fifo_int/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd fifo_int && $(MAKE)

cfg_int/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd cfg_int && $(MAKE)

orphan_int_column/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd orphan_int_column && $(MAKE)

clk_hrow/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd clk_hrow && $(MAKE)

clk_bufg/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd clk_bufg && $(MAKE)

hclk_cmt/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd hclk_cmt && $(MAKE)

hclk_ioi/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd hclk_ioi && $(MAKE)

build/tilegrid_tdb.json: add_tdb.py $(TILEGRID_TDB_DEPENDENCIES)
	python3 add_tdb.py \
		--fn-in build/basicdb/tilegrid.json \
		--fn-out build/tilegrid_tdb.json

build/tilegrid.json: generate_full.py build/tilegrid_tdb.json
	cd build && python3 ${FUZDIR}/generate_full.py \
        --json-in tilegrid_tdb.json --json-out ${BUILD_DIR}/tilegrid.json
run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build run.ok
	cd clb && $(MAKE) clean
	cd clb_int && $(MAKE) clean
	cd cfg && $(MAKE) clean
	cd iob && $(MAKE) clean
	cd iob_int && $(MAKE) clean
	cd ioi && $(MAKE) clean
	cd mmcm && $(MAKE) clean
	cd pll && $(MAKE) clean
	cd ps7_int && $(MAKE) clean
	cd bram && $(MAKE) clean
	cd bram_block && $(MAKE) clean
	cd bram_int && $(MAKE) clean
	cd dsp && $(MAKE) clean
	cd dsp_int && $(MAKE) clean
	cd fifo_int && $(MAKE) clean
	cd monitor && $(MAKE) clean
	cd monitor_int && $(MAKE) clean
	cd cfg_int && $(MAKE) clean
	cd orphan_int_column && $(MAKE) clean
	cd clk_hrow && $(MAKE) clean
	cd clk_bufg && $(MAKE) clean
	cd hclk_cmt && $(MAKE) clean
	cd hclk_ioi && $(MAKE) clean

.PHONY: database pushdb clean run

