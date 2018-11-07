
N := 1
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o seg_dsp_l.segbits $(addsuffix /segdata_dsp_l_*.txt,$(SPECIMENS))
	${XRAY_SEGMATCH} -o seg_dsp_r.segbits $(addsuffix /segdata_dsp_r_*.txt,$(SPECIMENS))

pushdb:
	${XRAY_MERGEDB} dsp_l seg_dsp_l.segbits
	${XRAY_MERGEDB} dsp_r seg_dsp_r.segbits
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
	rm -rf specimen_[0-9][0-9][0-9]/ seg_dsp_l.segbits seg_dsp_r.segbits run.ok

.PHONY: database pushdb run clean

