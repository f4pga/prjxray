# SLICEM takes a while to converge
N := 10
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: database/clbll database/clblm

pushdb: pushdb/clbll pushdb/clblm

database/%: $(SPECIMENS_OK)
	../../tools/segmatch -o seg_$(notdir $@).segbits \
			$(addsuffix /segdata_$(notdir $@).txt,$(SPECIMENS))

pushdb/%:
	bash ../../utils/mergedb.sh seg_$(notdir $@).segbits \
			../../database/$(XRAY_DATABASE)/seg_$(notdir $@).segbits

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ tilegrid.json vivado*.log vivado*.jou

.PHONY: database pushdb clean

