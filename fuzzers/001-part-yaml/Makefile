N := 1
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))

database: $(SPECIMENS)
	mkdir -p build
	cp build/specimen_001/part.yaml build/part.yaml
	python3 -m utils.xyaml build/part.yaml > build/part_no_iobanks.json
	python3 add_iobanks.py --part_json build/part_no_iobanks.json --iobanks_info build/specimen_001/iobanks.txt > build/part.json
	cp ${XRAY_PART}_required_features.fasm build/ 2>/dev/null || true

$(SPECIMENS): Makefile.specimen
	mkdir -p $@
	$(MAKE) -C $@ -f ../../Makefile.specimen

pushdb:
	cp build/part.yaml ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/${XRAY_PART}.yaml
	cp build/part.json ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/${XRAY_PART}.json
	cp build/${XRAY_PART}_required_features.fasm ${XRAY_DATABASE_DIR}/$(XRAY_DATABASE)/${XRAY_PART}_required_features.fasm 2>/dev/null || true

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build run.ok

.PHONY: database pushdb clean run $(SPECIMENS)
