
N := 1
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	true

pushdb:
	cp output/tile_type_*.json ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/
	rm ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/tile_type_*_site_type_*.json
	cp output/site_type_*.json ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/
	cp output/tileconn.json ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ output/ run.ok

.PHONY: database pushdb run clean

