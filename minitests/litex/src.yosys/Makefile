BASE_PATH = $(abspath $(PWD)/../../../)
YOSYS = $(BASE_PATH)/third_party/yosys/yosys
VIVADO = /opt/Xilinx/Vivado/2017.2/bin/vivado
PART = xc7a35tcsg324-1
BIT2FASM_ARGS = --db-root "$(BASE_PATH)/database/artix7" --part "$(BASE_PATH)/database/artix7/$(PART)" --verbose

all: top.fasm

clean:
	@rm -f *.edif
	@rm -f *.bit
	@rm -f *.fasm
	@rm -f *.log
	@rm -rf build

.PHONY: all clean

$(YOSYS):
	cd $(BASE_PATH)/third_party/yosys && make config-gcc && make -j$(shell nproc)

top.edif: $(YOSYS)
	$(YOSYS) -s synth.ys -l yosys.log

top.bit: $(VIVADO) top.edif
	mkdir -p build
	cd build && $(VIVADO) -mode batch -source ../top.tcl -nojournal -tempDir build -log vivado.log -verbose
	cp build/*.bit ./

top.fasm: top.bit
	PYTHONPATH="$(BASE_PATH):$(BASE_PATH)/utils:$(BASE_PATH)/third_party/fasm" \
    PATH="$(BASE_PATH)/build/tools:$(PATH)" \
    python3 \
        $(BASE_PATH)/utils/bit2fasm.py \
        $(BIT2FASM_ARGS) \
        top.bit >top.fasm \
        || (rm -f top.fasm && exit -1)
