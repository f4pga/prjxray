N := 8
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o seg_bramx.segbits.BLOCK_RAM $(addsuffix /segdata_bram_[lr].txt,$(SPECIMENS))

pushdb:
	${XRAY_MERGEDB} bram_l seg_bramx.segbits.BLOCK_RAM
	${XRAY_MERGEDB} bram_r seg_bramx.segbits.BLOCK_RAM

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_*.segbits vivado*.log vivado_*.str vivado*.jou design *.bits *.dcp *.bit top.v

.PHONY: database pushdb clean

