# read/write width is relatively slow to resolve
N := 2
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/seg_bramx.block_ram.segbits $(addsuffix /segdata_bram_[lr].txt,$(SPECIMENS))

pushdb:
	${XRAY_MERGEDB} bram_l.block_ram build/seg_bramx.block_ram.segbits
	${XRAY_MERGEDB} bram_r.block_ram build/seg_bramx.block_ram.segbits

build:
	mkdir build

$(SPECIMENS_OK): build
	bash generate.sh $(subst /OK,,$@)
	touch $@

clean:
	rm -rf build

.PHONY: database pushdb clean

