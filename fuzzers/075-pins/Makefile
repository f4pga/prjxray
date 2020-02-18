N := 1
BUILD_DIR = build_${XRAY_PART}
SPECIMENS := $(addprefix $(BUILD_DIR)/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)

pushdb:
	mkdir -p ${XRAY_FAMILY_DIR}/${XRAY_PART}/
	cp $(BUILD_DIR)/specimen_001/*_package_pins.csv ${XRAY_FAMILY_DIR}/${XRAY_PART}/package_pins.csv

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

run:
	rm -rf $(BUILD_DIR) run.${XRAY_PART}.ok
	$(MAKE) database
	$(MAKE) pushdb
	touch run.$(XRAY_PART).ok

clean:
	rm -rf build_* run.*.ok

.PHONY: database pushdb run clean
