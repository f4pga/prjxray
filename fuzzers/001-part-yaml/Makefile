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
	mkdir -p ${XRAY_FAMILY_DIR}/${XRAY_PART}
	cp build/part.json $(XRAY_FAMILY_DIR)/${XRAY_PART}/part.json
	cp build/part.yaml $(XRAY_FAMILY_DIR)/${XRAY_PART}/part.yaml
	cp build/${XRAY_PART}_required_features.fasm ${XRAY_FAMILY_DIR}/${XRAY_PART}/required_features.fasm 2>/dev/null || true

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build run.ok

.PHONY: database pushdb clean run $(SPECIMENS)
