
N := 1
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_dsp_l.db $(addsuffix /segdata_dsp_l_*.txt,$(SPECIMENS))
	${XRAY_SEGMATCH} -o build/segbits_dsp_r.db $(addsuffix /segdata_dsp_r_*.txt,$(SPECIMENS))
	${XRAY_DBFIXUP} --db-root build --clb-int

pushdb:
	${XRAY_MERGEDB} dsp_l build/segbits_dsp_l.db
	${XRAY_MERGEDB} dsp_r build/segbits_dsp_r.db

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build run.ok

.PHONY: database pushdb run clean

