database: build/tilegrid.json

pushdb:
	cp build/tilegrid.json ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/tilegrid.json

build/tilegrid.json: build/deltas
	cd build && python3 ../generate.py design_*.delta > tilegrid.json

build/deltas:
	bash generate.sh build

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build

.PHONY: database pushdb clean run

