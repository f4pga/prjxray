# TODO: parallelize

FUZDIR=$(shell pwd)
BUILD_DIR=$(FUZDIR)/build

database: build/tilegrid.json

pushdb:
	cp build/tilegrid.json ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/tilegrid.json

build/tiles/tiles.txt:
	bash generate.sh build/tiles tiles

build/tilegrid_basic.json: generate.py build/tiles/tiles.txt
	cd build && python3 ${FUZDIR}/generate.py --tiles $(FUZDIR)/build/tiles/tiles.txt --out ${BUILD_DIR}/tilegrid_basic.json

build/clb/deltas:
	bash generate.sh build/clb clb

build/bram/deltas:
	bash generate.sh build/bram bram

build/iob/deltas:
	bash generate.sh build/iob iob

build/tilegrid.json: generate_full.py build/tilegrid_basic.json build/clb/deltas build/bram/deltas build/iob/deltas
	cd build && python3 ${FUZDIR}/generate_full.py \
        --json-in tilegrid_basic.json --json-out ${BUILD_DIR}/tilegrid.json \
        --tiles $(FUZDIR)/build/tiles/tiles.txt */design_*.delta

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build

.PHONY: database pushdb clean run

