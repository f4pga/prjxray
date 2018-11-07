N := 1
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o seg_clblx.segbits $(addsuffix /segdata_clbl[lm]_[lr].txt,$(SPECIMENS))

pushdb:
	${XRAY_MERGEDB} clbll_l seg_clblx.segbits
	${XRAY_MERGEDB} clbll_r seg_clblx.segbits
	${XRAY_MERGEDB} clblm_l seg_clblx.segbits
	${XRAY_MERGEDB} clblm_r seg_clblx.segbits
	${XRAY_DBFIXUP} --clb-int

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ *.segbits vivado*.log vivado_*.str vivado*.jou design *.bits *.dcp *.bit top.v run.ok

.PHONY: database pushdb run clean

