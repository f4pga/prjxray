
N := 1
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	cp specimen_001/tilegrid.json tilegrid.json

pushdb:
	cp tilegrid.json ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/tilegrid.json

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ tilegrid.json run.ok

.PHONY: database pushdb clean run

