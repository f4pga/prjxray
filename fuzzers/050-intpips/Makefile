
N := 200
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -m 5 -M 15 -o seg_int_l.segbits $(addsuffix /segdata_int_l.txt,$(SPECIMENS))
	${XRAY_SEGMATCH} -m 5 -M 15 -o seg_int_r.segbits $(addsuffix /segdata_int_r.txt,$(SPECIMENS))
	${XRAY_MASKMERGE} mask_clbll_l.segbits $(addsuffix /segdata_int_l.txt,$(SPECIMENS))
	${XRAY_MASKMERGE} mask_clbll_r.segbits $(addsuffix /segdata_int_r.txt,$(SPECIMENS))
	${XRAY_MASKMERGE} mask_clblm_l.segbits $(addsuffix /segdata_int_l.txt,$(SPECIMENS))
	${XRAY_MASKMERGE} mask_clblm_r.segbits $(addsuffix /segdata_int_r.txt,$(SPECIMENS))

pushdb:
	${XRAY_MERGEDB} int_l seg_int_l.segbits
	${XRAY_MERGEDB} int_r seg_int_r.segbits
	${XRAY_MERGEDB} mask_clbll_l mask_clbll_l.segbits
	${XRAY_MERGEDB} mask_clbll_r mask_clbll_r.segbits
	${XRAY_MERGEDB} mask_clblm_l mask_clblm_l.segbits
	${XRAY_MERGEDB} mask_clblm_r mask_clblm_r.segbits
	${XRAY_DBFIXUP}

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_int_[lr].segbits mask_clbl[lm]_[lr].segbits run.ok

.PHONY: database pushdb run clean

