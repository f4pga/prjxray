BUILD_DIR=build
HARNESS_DIR ?= harness
export BUILD_DIR

XRAY_PINCFG ?= BASYS3-SWBUT
export XRAY_PINCFG

HARNESS_FILES=$(BUILD_DIR)/design.bit $(BUILD_DIR)/design.txt $(BUILD_DIR)/design.json $(BUILD_DIR)/design.dcp

# official demo configuration
all: $(HARNESS_FILES)

$(HARNESS_FILES): runme.sh runme.tcl
	./runme.sh

copy: $(HARNESS_FILES)
	mkdir -p $(HARNESS_DIR)
	cp $(HARNESS_FILES) $(HARNESS_DIR)

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_clblx.segbits vivado*.log vivado_*.str vivado*.jou design *.bits *.dcp *.bit design.txt .Xil
	rm -rf $(BUILD_DIR) *~

.PHONY: all clean copy

