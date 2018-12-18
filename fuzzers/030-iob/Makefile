N := 1
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_ioblx.db $(addsuffix /segdata_liob33.txt,$(SPECIMENS))

#pushdb:
#	${XRAY_MERGEDB} ioblm_l build/segbits_ioblx.db
#	${XRAY_MERGEDB} ioblm_r build/segbits_ioblx.db

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build

.PHONY: database pushdb run clean

