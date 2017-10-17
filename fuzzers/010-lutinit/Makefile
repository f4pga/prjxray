
include ../../settings.sh

N := 1
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	../../tools/segmatch -o lutbits.txt \
		$(addsuffix /segdata_0.txt,$(SPECIMENS)) \
		$(addsuffix /segdata_1.txt,$(SPECIMENS)) \
		$(addsuffix /segdata_2.txt,$(SPECIMENS))
	grep '^CLBLL_L\.' lutbits.txt | cut -f2- -d. | sort > seg_clbll_l.segbits
	grep '^CLBLL_R\.' lutbits.txt | cut -f2- -d. | sort > seg_clbll_r.segbits
	grep '^CLBLM_L\.' lutbits.txt | cut -f2- -d. | sort > seg_clblm_l.segbits
	grep '^CLBLM_R\.' lutbits.txt | cut -f2- -d. | sort > seg_clblm_r.segbits
	cmp seg_clbll_l.segbits seg_clbll_r.segbits
	cmp seg_clblm_l.segbits seg_clblm_r.segbits

pushdb/%:
	touch ../../database/$(XRAY_DATABASE)/seg_$(notdir $@).segbits
	sort -u ../../database/$(XRAY_DATABASE)/seg_$(notdir $@).segbits \
			seg_$(notdir $@)_?.segbits  > seg_$(notdir $@).segbits
	cp seg_$(notdir $@).segbits ../../database/$(XRAY_DATABASE)/seg_$(notdir $@).segbits

pushdb: pushdb/clbll pushdb/clblm

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

clean:
	rm -rf $(SPECIMENS)

.PHONY: database pushdb clean

