
N := 1
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	cp build/specimen_001/ppips_*.db build/

pushdb:
	cp build/ppips_*.db ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

run.ok: run

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build run.ok

.PHONY: database pushdb run clean

