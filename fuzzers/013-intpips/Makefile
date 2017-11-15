
N := 200
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -m 5 -M 15 -o seg_clbll_int_l.segbits $(addsuffix /segdata_clbll_l.txt,$(SPECIMENS))
	${XRAY_SEGMATCH} -m 5 -M 15 -o seg_clbll_int_r.segbits $(addsuffix /segdata_clbll_r.txt,$(SPECIMENS))
	${XRAY_SEGMATCH} -m 5 -M 15 -o seg_clblm_int_l.segbits $(addsuffix /segdata_clblm_l.txt,$(SPECIMENS))
	${XRAY_SEGMATCH} -m 5 -M 15 -o seg_clblm_int_r.segbits $(addsuffix /segdata_clblm_r.txt,$(SPECIMENS))
	grep -h ^bit $(addsuffix /segdata_clbll_l.txt,$(SPECIMENS)) | sort -u > seg_clbll_mask_l.segbits
	grep -h ^bit $(addsuffix /segdata_clbll_r.txt,$(SPECIMENS)) | sort -u > seg_clbll_mask_r.segbits
	grep -h ^bit $(addsuffix /segdata_clblm_l.txt,$(SPECIMENS)) | sort -u > seg_clblm_mask_l.segbits
	grep -h ^bit $(addsuffix /segdata_clblm_r.txt,$(SPECIMENS)) | sort -u > seg_clblm_mask_r.segbits

pushdb:
	${XRAY_MERGEDB} clbll_int_l seg_clbll_int_l.segbits
	${XRAY_MERGEDB} clbll_int_r seg_clbll_int_r.segbits
	${XRAY_MERGEDB} clblm_int_l seg_clblm_int_l.segbits
	${XRAY_MERGEDB} clblm_int_r seg_clblm_int_r.segbits
	${XRAY_MERGEDB} clbll_mask_l seg_clbll_mask_l.segbits
	${XRAY_MERGEDB} clbll_mask_r seg_clbll_mask_r.segbits
	${XRAY_MERGEDB} clblm_mask_l seg_clblm_mask_l.segbits
	${XRAY_MERGEDB} clblm_mask_r seg_clblm_mask_r.segbits

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_clbl[lm]_int_[lr].segbits seg_clbl[lm]_mask_[lr].segbits

.PHONY: database pushdb clean

