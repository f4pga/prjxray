N := 1
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))

database: $(SPECIMENS)
	cp specimen_001/part.yaml ${XRAY_PART}.yaml

$(SPECIMENS): Makefile.specimen
	mkdir -p $@
	$(MAKE) -C $@ -f ../Makefile.specimen

pushdb:
	cp ${XRAY_PART}.yaml ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)
	python -m utils.xyaml ${XRAY_PART}.yaml > ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/${XRAY_PART}.json

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ *.yaml run.ok

.PHONY: database pushdb clean run $(SPECIMENS)
