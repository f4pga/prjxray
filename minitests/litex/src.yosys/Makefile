VIVADO = /opt/Xilinx/Vivado/2017.2/bin/vivado

all: top.bit

clean:
	@rm -f *.edif
	@rm -f *.bit
	@rm -f *.log
	@rm -rf build

.PHONY: all clean

top.edif: $(YOSYS)
	$(YOSYS) -s synth.ys -l yosys.log

top.bit: $(VIVADO) top.edif
	mkdir -p build
	cd build && $(VIVADO) -mode batch -source ../top.tcl -nojournal -tempDir build -log vivado.log -verbose
	cp build/*.bit ./
