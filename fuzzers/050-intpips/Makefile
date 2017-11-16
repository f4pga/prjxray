
N := 200
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -m 5 -M 15 -o seg_int_l.segbits $(addsuffix /segdata_clbl[lm]_l.txt,$(SPECIMENS))
	${XRAY_SEGMATCH} -m 5 -M 15 -o seg_int_r.segbits $(addsuffix /segdata_clbl[lm]_r.txt,$(SPECIMENS))
	grep -h ^bit $(addsuffix /segdata_clbll_l.txt,$(SPECIMENS)) | sort -u > mask_clbll_l.segbits
	grep -h ^bit $(addsuffix /segdata_clbll_r.txt,$(SPECIMENS)) | sort -u > mask_clbll_r.segbits
	grep -h ^bit $(addsuffix /segdata_clblm_l.txt,$(SPECIMENS)) | sort -u > mask_clblm_l.segbits
	grep -h ^bit $(addsuffix /segdata_clblm_r.txt,$(SPECIMENS)) | sort -u > mask_clblm_r.segbits

pushdb:
	${XRAY_MERGEDB} int_l seg_int_l.segbits
	${XRAY_MERGEDB} int_r seg_int_r.segbits
	${XRAY_MERGEDB} mask_clbll_l mask_clbll_l.segbits
	${XRAY_MERGEDB} mask_clbll_r mask_clbll_r.segbits
	${XRAY_MERGEDB} mask_clblm_l mask_clblm_l.segbits
	${XRAY_MERGEDB} mask_clblm_r mask_clblm_r.segbits

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_clbl[lm]_int_[lr].segbits seg_clbl[lm]_mask_[lr].segbits

.PHONY: database pushdb clean

