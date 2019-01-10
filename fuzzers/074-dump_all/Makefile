
N := 1
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	true

pushdb:
	cp build/output/tile_type_*.json ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/
	rm ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/tile_type_*_site_type_*.json
	cp build/output/site_type_*.json ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/
	cp build/output/tileconn.json ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build run.ok

.PHONY: database pushdb run clean

