BASE_PATH = $(abspath $(PWD)/../../../)
VIVADO = $(BASE_PATH)/utils/vivado.sh
PART = xc7a35tcsg324-1
BIT2FASM_ARGS = --db-root "$(BASE_PATH)/database/artix7" --part "$(BASE_PATH)/database/artix7/$(PART)" --verbose

all: top.fasm

clean:
	@rm -f *.bit
	@rm -f *.fasm
	@rm -rf build

.PHONY: all clean

top.bit: $(VIVADO)
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
