VIVADO = /opt/Xilinx/Vivado/2017.2/bin/vivado

all: top.bit

clean:
	@rm -f *.bit
	@rm -rf build

.PHONY: all clean

top.bit: $(VIVADO)
	mkdir -p build
	cd build && $(VIVADO) -mode batch -source ../top.tcl -nojournal -tempDir build -log vivado.log -verbose
	cp build/*.bit ./
