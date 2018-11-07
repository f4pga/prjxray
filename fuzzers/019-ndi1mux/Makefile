# clb.mk clblm only

N := 1
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/seg_clblx.segbits $(addsuffix /segdata_clblm_[lr].txt,$(SPECIMENS))

pushdb:
	${XRAY_MERGEDB} clblm_l build/seg_clblx.segbits
	${XRAY_MERGEDB} clblm_r build/seg_clblx.segbits

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

.PHONY: database pushdb run clean

