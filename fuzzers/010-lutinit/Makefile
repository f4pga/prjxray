# NOt using clb.mk: 0-2 segmatch
# Could probably change segmatch to re though

N := 1
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o seg_clbll.segbits $(addsuffix /segdata_clbll_[lr]_[012].txt,$(SPECIMENS))
	${XRAY_SEGMATCH} -o seg_clblm.segbits $(addsuffix /segdata_clblm_[lr]_[012].txt,$(SPECIMENS))

pushdb:
	${XRAY_MERGEDB} clbll_l seg_clbll.segbits
	${XRAY_MERGEDB} clbll_r seg_clbll.segbits
	${XRAY_MERGEDB} clblm_l seg_clblm.segbits
	${XRAY_MERGEDB} clblm_r seg_clblm.segbits

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_clbll.segbits seg_clblm.segbits run.ok

.PHONY: database pushdb run clean

