N ?= 10
GENERATE_ARGS ?=
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: build/segbits_tilegrid.tdb

build/segbits_tilegrid.tdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_tilegrid.tdb $$(find build -name "segdata_tilegrid.txt")

$(SPECIMENS_OK):
	GENERATE_ARGS=${GENERATE_ARGS} bash ../fuzzaddr/generate.sh $(subst /OK,,$@)
	touch $@

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build

.PHONY: database pushdb run clean

