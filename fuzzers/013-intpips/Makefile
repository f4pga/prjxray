
N := 200
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	../../tools/segmatch -m 5 -M 15 -o seg_clbll_int_l.segbits $(addsuffix /segdata_clbll_l.txt,$(SPECIMENS))
	../../tools/segmatch -m 5 -M 15 -o seg_clbll_int_r.segbits $(addsuffix /segdata_clbll_r.txt,$(SPECIMENS))
	../../tools/segmatch -m 5 -M 15 -o seg_clblm_int_l.segbits $(addsuffix /segdata_clblm_l.txt,$(SPECIMENS))
	../../tools/segmatch -m 5 -M 15 -o seg_clblm_int_r.segbits $(addsuffix /segdata_clblm_r.txt,$(SPECIMENS))

pushdb:
	bash ../../utils/mergedb.sh clbll_int_l seg_clbll_int_l.segbits
	bash ../../utils/mergedb.sh clbll_int_r seg_clbll_int_r.segbits
	bash ../../utils/mergedb.sh clblm_int_l seg_clblm_int_l.segbits
	bash ../../utils/mergedb.sh clblm_int_r seg_clblm_int_r.segbits

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_clbl[lm]_int_[lr].segbits

.PHONY: database pushdb clean

