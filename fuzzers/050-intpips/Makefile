
N := 200
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -m 5 -M 15 -o build/seg_int_l.segbits $(addsuffix /segdata_int_l.txt,$(SPECIMENS))
	${XRAY_SEGMATCH} -m 5 -M 15 -o build/seg_int_r.segbits $(addsuffix /segdata_int_r.txt,$(SPECIMENS))
	${XRAY_MASKMERGE} build/mask_clbll_l.segbits $(addsuffix /segdata_int_l.txt,$(SPECIMENS))
	${XRAY_MASKMERGE} build/mask_clbll_r.segbits $(addsuffix /segdata_int_r.txt,$(SPECIMENS))
	${XRAY_MASKMERGE} build/mask_clblm_l.segbits $(addsuffix /segdata_int_l.txt,$(SPECIMENS))
	${XRAY_MASKMERGE} build/mask_clblm_r.segbits $(addsuffix /segdata_int_r.txt,$(SPECIMENS))

pushdb:
	${XRAY_DBFIXUP} --db-root build --clb-int
	${XRAY_MERGEDB} int_l build/seg_int_l.segbits
	${XRAY_MERGEDB} int_r build/seg_int_r.segbits
	${XRAY_MERGEDB} mask_clbll_l build/mask_clbll_l.segbits
	${XRAY_MERGEDB} mask_clbll_r build/mask_clbll_r.segbits
	${XRAY_MERGEDB} mask_clblm_l build/mask_clblm_l.segbits
	${XRAY_MERGEDB} mask_clblm_r build/mask_clblm_r.segbits

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

