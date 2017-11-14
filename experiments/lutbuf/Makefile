N := 1
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	../../tools/segmatch -o seg_clblx.segbits $(addsuffix /segdata_clbl[lm]_[lr].txt,$(SPECIMENS))

pushdb:
	bash ../../utils/mergedb.sh clbll_l seg_clblx.segbits
	bash ../../utils/mergedb.sh clbll_r seg_clblx.segbits
	bash ../../utils/mergedb.sh clblm_l seg_clblx.segbits
	bash ../../utils/mergedb.sh clblm_r seg_clblx.segbits

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_clblx.segbits

.PHONY: database pushdb clean

