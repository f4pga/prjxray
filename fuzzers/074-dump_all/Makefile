
N := 1
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
MAX_VIVADO_PROCESS ?= 4
MAX_TILES_INSTANCE ?= 300
MAX_NODES_INSTANCE ?= 30000

database: $(SPECIMENS_OK)
	true

pushdb:
	cp build/output/tile_type_*.json ${XRAY_FAMILY_DIR}/
	rm ${XRAY_FAMILY_DIR}/tile_type_*_site_type_*.json
	cp build/output/site_type_*.json ${XRAY_FAMILY_DIR}/
	cp build/output/tileconn.json ${XRAY_FAMILY_DIR}/$(XRAY_PART)/

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@) -p=$(MAX_VIVADO_PROCESS) -t=$(MAX_TILES_INSTANCE) -n=$(MAX_NODES_INSTANCE)
	touch $@

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build run.ok

.PHONY: database pushdb run clean

