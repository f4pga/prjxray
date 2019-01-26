FUZDIR=$(shell pwd)
BUILD_DIR=$(FUZDIR)/build
TILEGRID_TDB_DEPENDENCIES=
TILEGRID_TDB_DEPENDENCIES += iob/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += iob_int/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += mmcm/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += pll/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += monitor/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += bram/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += bram_block/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += bram_int/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += clb/build/segbits_tilegrid.tdb
TILEGRID_TDB_DEPENDENCIES += clb_int/build/segbits_tilegrid.tdb
GENERATE_FULL_ARGS=

ifeq (${XRAY_DATABASE}, zynq7)
TILEGRID_TDB_DEPENDENCIES += ps7_int/build/segbits_tilegrid.tdb
GENERATE_FULL_ARGS += --int-tdb $(FUZDIR)/ps7_int/build/segbits_tilegrid.tdb
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

iob/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd iob && $(MAKE)

iob_int/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd iob_int && $(MAKE)

mmcm/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd mmcm && $(MAKE)

pll/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd pll && $(MAKE)

ps7_int/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd ps7_int && $(MAKE)

monitor/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd monitor && $(MAKE)

bram/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd bram && $(MAKE)

bram_block/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd bram_block && $(MAKE)

bram_int/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd bram_int && $(MAKE)

build/tilegrid_tdb.json: add_tdb.py $(TILEGRID_TDB_DEPENDENCIES)
	python3 add_tdb.py \
		--fn-in build/basicdb/tilegrid.json \
		--fn-out build/tilegrid_tdb.json

build/tilegrid.json: generate_full.py build/tilegrid_tdb.json
	cd build && python3 ${FUZDIR}/generate_full.py \
        --json-in tilegrid_tdb.json --json-out ${BUILD_DIR}/tilegrid.json \
        --tiles $(FUZDIR)/build/tiles/tiles.txt ${GENERATE_FULL_ARGS}
run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build run.ok
	cd clb && $(MAKE) clean
	cd clb_int && $(MAKE) clean
	cd iob && $(MAKE) clean
	cd iob_int && $(MAKE) clean
	cd mmcm && $(MAKE) clean
	cd pll && $(MAKE) clean
	cd ps7_int && $(MAKE) clean
	cd bram && $(MAKE) clean
	cd bram_block && $(MAKE) clean
	cd bram_int && $(MAKE) clean
	cd monitor && $(MAKE) clean

.PHONY: database pushdb clean run

