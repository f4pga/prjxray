N := 15
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: build/segbits_tilegrid.tdb

build/segbits_tilegrid.tdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_tilegrid.tdb $$(find build -name "segdata_tilegrid.txt")

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build

.PHONY: database pushdb run clean

