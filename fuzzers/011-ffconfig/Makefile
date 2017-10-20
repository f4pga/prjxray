
N := 3
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: database/clbll database/clblm

pushdb: pushdb/clbll pushdb/clblm

database/%: $(SPECIMENS_OK)
	../../tools/segmatch -o seg_$(notdir $@).segbits \
			$(addsuffix /segdata_$(notdir $@)_[0-9].txt,$(SPECIMENS))

pushdb/%:
	bash ../../utils/mergedb.sh seg_$(notdir $@).segbits \
			../../database/$(XRAY_DATABASE)/seg_$(notdir $@).segbits

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

regen:
	set -ex; for d in $(SPECIMENS); do cd $$d; for i in 0 1 2 3 4 5 6 7 8 9; do python3 ../generate.py $$i; done; cd ..; done

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_clbll.segbits seg_clblm.segbits

.PHONY: database pushdb regen clean

