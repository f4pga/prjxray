
N := 1
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o segbits_dsp_l.db $(addsuffix /segdata_dsp_l_*.txt,$(SPECIMENS))
	${XRAY_SEGMATCH} -o segbits_dsp_r.db $(addsuffix /segdata_dsp_r_*.txt,$(SPECIMENS))

pushdb:
	${XRAY_DBFIXUP} --db-root . --clb-int
	${XRAY_MERGEDB} dsp_l segbits_dsp_l.db
	${XRAY_MERGEDB} dsp_r segbits_dsp_r.db

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ segbits_dsp_l.db segbits_dsp_r.db run.ok

.PHONY: database pushdb run clean

