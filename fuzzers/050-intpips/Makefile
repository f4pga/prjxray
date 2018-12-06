ifeq ($(QUICK),Y)
N := 1
else
N := 200
endif

SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -m 5 -M 15 -o build/segbits_int_l.db $(addsuffix /segdata_int_l.txt,$(SPECIMENS))
	${XRAY_SEGMATCH} -m 5 -M 15 -o build/segbits_int_r.db $(addsuffix /segdata_int_r.txt,$(SPECIMENS))
	${XRAY_MASKMERGE} build/mask_clbll_l.db $(addsuffix /segdata_int_l.txt,$(SPECIMENS))
	${XRAY_MASKMERGE} build/mask_clbll_r.db $(addsuffix /segdata_int_r.txt,$(SPECIMENS))
	${XRAY_MASKMERGE} build/mask_clblm_l.db $(addsuffix /segdata_int_l.txt,$(SPECIMENS))
	${XRAY_MASKMERGE} build/mask_clblm_r.db $(addsuffix /segdata_int_r.txt,$(SPECIMENS))
	${XRAY_DBFIXUP} --db-root build --clb-int

pushdb:
	${XRAY_MERGEDB} int_l build/segbits_int_l.db
	${XRAY_MERGEDB} int_r build/segbits_int_r.db
	${XRAY_MERGEDB} mask_clbll_l build/mask_clbll_l.db
	${XRAY_MERGEDB} mask_clbll_r build/mask_clbll_r.db
	${XRAY_MERGEDB} mask_clblm_l build/mask_clblm_l.db
	${XRAY_MERGEDB} mask_clblm_r build/mask_clblm_r.db

$(SPECIMENS_OK):
	mkdir -p build
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

