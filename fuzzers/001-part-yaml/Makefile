N := 1
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))

database: $(SPECIMENS)
	mkdir -p build
	cp build/specimen_001/part.yaml build/part.yaml
	python3 -m utils.xyaml build/part.yaml > build/part.json

$(SPECIMENS): Makefile.specimen
	mkdir -p $@
	$(MAKE) -C $@ -f ../../Makefile.specimen

pushdb:
	cp build/part.yaml ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)
	cp build/part.json ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build run.ok

.PHONY: database pushdb clean run $(SPECIMENS)
