
N := 1
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	../../tools/segmatch -o seg_clbll.segbits $(addsuffix /segdata_clbll_[lr]_[012].txt,$(SPECIMENS))
	../../tools/segmatch -o seg_clblm.segbits $(addsuffix /segdata_clblm_[lr]_[012].txt,$(SPECIMENS))

pushdb:
	bash ../../utils/mergedb.sh clbll_l seg_clbll.segbits
	bash ../../utils/mergedb.sh clbll_r seg_clbll.segbits
	bash ../../utils/mergedb.sh clblm_l seg_clblm.segbits
	bash ../../utils/mergedb.sh clblm_r seg_clblm.segbits

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_clbll.segbits seg_clblm.segbits

.PHONY: database pushdb clean

