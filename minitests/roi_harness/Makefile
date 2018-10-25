BUILD_DIR=build
export BUILD_DIR

XRAY_PINCFG ?= BASYS3-SWBUT
export XRAY_PINCFG

# official demo configuration
all:
	./runme.sh

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_clblx.segbits vivado*.log vivado_*.str vivado*.jou design *.bits *.dcp *.bit design.txt .Xil
	rm -rf $(BUILD_DIR) *~

.PHONY: all clean

