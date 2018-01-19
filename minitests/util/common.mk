all:
	bash $$XRAY_DIR/minitests/util/runme.sh

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_clblx.segbits vivado*.log vivado_*.str vivado*.jou design *.bits *.dcp *.bit design.txt .Xil

.PHONY: all clean

