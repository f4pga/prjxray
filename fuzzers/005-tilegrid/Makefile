# TODO: parallelize

FUZDIR=$(shell pwd)
BUILD_DIR=$(FUZDIR)/build

database: build/tilegrid.json

pushdb:
	cp build/tilegrid.json ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/tilegrid.json

build/tiles/tiles.txt:
	bash generate.sh build/tiles tiles

build/basicdb/tilegrid.json: generate.py build/tiles/tiles.txt
	mkdir -p build/basicdb
	cd build && python3 ${FUZDIR}/generate.py --tiles $(FUZDIR)/build/tiles/tiles.txt --out ${BUILD_DIR}/basicdb/tilegrid.json

build/clb/deltas:
	bash generate.sh build/clb clb

build/bram/deltas:
	bash generate.sh build/bram bram

# FIXME: review IOB
build/iob/deltas:
	bash generate.sh build/iob iob

build/tilegrid_tdb.json: iob/build/segbits_tilegrid.tdb
	python3 add_tdb.py --fn-in build/basicdb/tilegrid.json --fn-out build/tilegrid_tdb.json

iob/build/segbits_tilegrid.tdb: build/basicdb/tilegrid.json
	cd iob && $(MAKE)

# FIXME: review IOB
build/tilegrid.json: generate_full.py build/tilegrid_tdb.json build/clb/deltas build/bram/deltas
	cd build && python3 ${FUZDIR}/generate_full.py \
        --json-in tilegrid_tdb.json --json-out ${BUILD_DIR}/tilegrid.json \
        --tiles $(FUZDIR)/build/tiles/tiles.txt {clb,bram}/design_*.delta

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build
	cd iob && $(MAKE) clean

.PHONY: database pushdb clean run

