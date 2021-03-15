N ?= 10
BUILD_DIR = build_$(XRAY_PART)
GENERATE_ARGS ?=
SPECIMENS := $(addprefix $(BUILD_DIR)/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(BUILD_DIR)/segbits_tilegrid.tdb

$(BUILD_DIR)/segbits_tilegrid.tdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o $(BUILD_DIR)/segbits_tilegrid.tdb $$(find $(BUILD_DIR) -name "segdata_tilegrid.txt")

$(SPECIMENS_OK):
	GENERATE_ARGS=${GENERATE_ARGS} bash ../fuzzaddr/generate.sh $(subst /OK,,$@)
	touch $@

clean:
	rm -rf build_*

clean_part:
	rm -rf $(BUILD_DIR)

.PHONY: database clean

