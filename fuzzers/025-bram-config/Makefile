# read/write width is relatively slow to resolve
N := 4
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/seg_bramx.segbits $(addsuffix /segdata_bram_[lr].txt,$(SPECIMENS))

pushdb:
	${XRAY_MERGEDB} bram_l build/seg_bramx.segbits
	${XRAY_MERGEDB} bram_r build/seg_bramx.segbits

build:
	mkdir build

$(SPECIMENS_OK): build
	bash generate.sh $(subst /OK,,$@)
	touch $@

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build

.PHONY: database pushdb clean

