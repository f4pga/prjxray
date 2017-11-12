
N := 200
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	../../tools/segmatch -m 5 -M 15 -o seg_clbll_int.segbits \
			$(addsuffix /segdata_clbll.txt,$(SPECIMENS))
	../../tools/segmatch -m 5 -M 15 -o seg_clblm_int.segbits \
			$(addsuffix /segdata_clblm.txt,$(SPECIMENS))

pushdb:
	bash ../../utils/mergedb.sh seg_clbll_int.segbits \
			../../database/$(XRAY_DATABASE)/seg_clbll_int.segbits
	bash ../../utils/mergedb.sh seg_clblm_int.segbits \
			../../database/$(XRAY_DATABASE)/seg_clblm_int.segbits

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_clbll.segbits seg_clblm.segbits

.PHONY: database pushdb clean

