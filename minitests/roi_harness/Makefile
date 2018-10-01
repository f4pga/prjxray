BUILD_DIR=build

# official demo configuration
all:
	SMALL=Y BUILD_DIR=$(BUILD_DIR) XRAY_PINCFG=BASYS3-SWBUT ./runme.sh

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_clblx.segbits vivado*.log vivado_*.str vivado*.jou design *.bits *.dcp *.bit design.txt .Xil
	rm -rf $(BUILD_DIR) *~

.PHONY: all clean

