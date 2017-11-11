
N := 15
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	../../tools/segmatch -m 5 -M 15 -o seg_int.segbits \
			$(addsuffix /segdata_clbll.txt,$(SPECIMENS)) \
			$(addsuffix /segdata_clblm.txt,$(SPECIMENS))

pushdb:
	bash ../../utils/mergedb.sh seg_int.segbits \
			../../database/$(XRAY_DATABASE)/seg_int.segbits

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_clbll.segbits seg_clblm.segbits

.PHONY: database pushdb clean

