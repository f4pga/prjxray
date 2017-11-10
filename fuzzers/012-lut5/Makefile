
N := 1
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	#cp specimen_001/tilegrid.json tilegrid.json
	true

pushdb:
	cp tilegrid.json ../../database/$(XRAY_DATABASE)/tilegrid.json

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ tilegrid.json vivado*.log vivado*.jou

.PHONY: database pushdb clean

