N := 1
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_clblx.db $(addsuffix /segdata_clbl[lm]_[lr].txt,$(SPECIMENS))

pushdb:
	$(DBFIXUP)
	${XRAY_MERGEDB} clbll_l build/segbits_clblx.db
	${XRAY_MERGEDB} clbll_r build/segbits_clblx.db
	${XRAY_MERGEDB} clblm_l build/segbits_clblx.db
	${XRAY_MERGEDB} clblm_r build/segbits_clblx.db

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

