BASE_PATH = $(abspath $(PWD)/../../../)
YOSYS = $(BASE_PATH)/third_party/yosys/yosys
PART = xc7a35tcsg324-1
BIT2FASM_ARGS = --part "$(BASE_PATH)/database/artix7/$(PART)" --verbose

all: top.fasm top.bits segprint.log

clean:
	@rm -f *.edif
	@rm -f *.bit
	@rm -f *.bin
	@rm -f *.bits
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
	cd build && $(XRAY_VIVADO) -mode batch -source ../top.tcl -nojournal -tempDir build -log vivado.log -verbose
	cp build/*.bit ./

top.fasm: top.bit
	PYTHONPATH="$(BASE_PATH):$(BASE_PATH)/utils:$(BASE_PATH)/third_party/fasm" \
    PATH="$(BASE_PATH)/build/tools:$(PATH)" \
    $(XRAY_BIT2FASM) $(BIT2FASM_ARGS) \
        top.bit >top.fasm \
        || (rm -f top.fasm && exit -1)

top.bits: top.bit
	$(XRAY_BITREAD) -part_file $(BASE_PATH)/database/artix7/$(PART).yaml -o top.bits -z -y top.bit

segprint.log: top.bits
	$(XRAY_SEGPRINT) -z -D -b top.bits > segprint.log
