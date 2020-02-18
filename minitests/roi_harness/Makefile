XRAY_PINCFG ?= BASYS3-SWBUT
export XRAY_PINCFG

BUILD_DIR=build_$(XRAY_PINCFG)
HARNESS_DIR ?= harness_$(XRAY_PINCFG)
export BUILD_DIR

HARNESS_FILES=$(BUILD_DIR)/design.bit $(BUILD_DIR)/design.txt $(BUILD_DIR)/design.json $(BUILD_DIR)/design.dcp

# official demo configuration
all: $(BUILD_DIR)/run.ok

$(BUILD_DIR)/run.ok: runme.sh runme.tcl
	./runme.sh
	touch $(BUILD_DIR)/run.ok

copy: $(BUILD_DIR)/run.ok
	mkdir -p $(HARNESS_DIR)
	cp $(HARNESS_FILES) $(HARNESS_DIR)

clean:
	rm -rf build_* harness_*

run:
	make clean
	make copy

.PHONY: all clean copy run
