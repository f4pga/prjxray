N := 1
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))

.PHONY: database pushdb clean $(SPECIMENS)

$(SPECIMENS): Makefile.specimen
	mkdir -p $@
	$(MAKE) -C $@ -f ../Makefile.specimen

database: $(SPECIMENS)
	cp specimen_001/part.yaml ${XRAY_PART}.yaml

pushdb:
	cp ${XRAY_PART}.yaml ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ *.yaml
