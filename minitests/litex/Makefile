BASE_PATH = $(abspath $(PWD)/../../)
THIRD_PARTY = $(BASE_PATH)/third_party
YOSYS_PATH = $(THIRD_PARTY)/yosys
CROSS_PATH = $(THIRD_PARTY)/crosstool-ng
CROSS_TOOL = $(CROSS_PATH)/riscv32-unknown-elf/bin
LITEX_ARGS = --cpu-type vexriscv --with-ethernet --no-compile-software
BIT2FASM_ARGS = --db-root "$(BASE_PATH)/database/artix7" --part "$(BASE_PATH)/database/artix7/$(PART)" --verbose
PART = xc7a35tcsg324-1

all: soc_basesoc_arty_yosys soc_basesoc_arty_vivado

clean:
	rm -f yosys.ok
	rm -f toolchain.ok
	rm -rf soc_basesoc_arty_yosys
	rm -rf soc_basesoc_arty_vivado
	rm -f soc_basesoc_arty_yosys.fasm
	rm -f soc_basesoc_arty_vivado.fasm

.PHONY: all clean soc_basesoc_arty_yosys soc_basesoc_arty_vivado

#  ------------ toolchain -------------

toolchain.ok:
	./build_toolchain.sh
	touch toolchain.ok

yosys.ok:
	./build_yosys.sh
	touch yosys.ok

# -------------- LiteX ----------------

soc_basesoc_arty_yosys: soc_basesoc_arty_yosys/software soc_basesoc_arty_yosys/gateware/top.bit soc_basesoc_arty_yosys.fasm

soc_basesoc_arty_vivado: soc_basesoc_arty_vivado/software soc_basesoc_arty_vivado/gateware/top.bit soc_basesoc_arty_vivado.fasm

soc_basesoc_arty_yosys/software soc_basesoc_arty_yosys/gateware/top.bit: toolchain.ok yosys.ok
	PYTHONPATH="$(THIRD_PARTY)/migen:$(THIRD_PARTY)/litex:$(THIRD_PARTY)/litedram:$(THIRD_PARTY)/liteeth" \
	PATH="$(YOSYS_PATH):$(CROSS_TOOL):$(PATH)" \
	python3 \
		$(THIRD_PARTY)/litex/litex/boards/targets/arty.py \
        --synth-mode "yosys" \
		--output-dir=soc_basesoc_arty_yosys \
		$(LITEX_ARGS)

soc_basesoc_arty_vivado/software soc_basesoc_arty_vivado/gateware/top.bit: toolchain.ok
	PYTHONPATH="$(PWD)/migen:$(PWD)/litex:$(PWD)/litedram:$(PWD)/liteeth" \
	PATH="$(YOSYS_PATH):$(CROSS_TOOL):$(PATH)" \
	python3 \
		$(THIRD_PARTY)/litex/litex/boards/targets/arty.py \
        --synth-mode "vivado" \
		--output-dir=soc_basesoc_arty_vivado \
		$(LITEX_ARGS)

# -------------- bit2fasm -------------

soc_basesoc_arty_yosys.fasm:
	PYTHONPATH="$(BASE_PATH):$(BASE_PATH)/utils:$(BASE_PATH)/third_party/fasm" \
	PATH="$(BASE_PATH)/build/tools:$(PATH)" \
	python3 \
		../../utils/bit2fasm.py \
		$(BIT2FASM_ARGS) \
		soc_basesoc_arty_yosys/gateware/top.bit \
		>soc_basesoc_arty_yosys.fasm \
		|| (rm -f soc_basesoc_arty_yosys.fasm && exit -1)

soc_basesoc_arty_vivado.fasm:
	PYTHONPATH="$(BASE_PATH):$(BASE_PATH)/utils:$(BASE_PATH)/third_party/fasm" \
	PATH="$(BASE_PATH)/build/tools:$(PATH)" \
	python3 \
		../../utils/bit2fasm.py \
		$(BIT2FASM_ARGS) \
		soc_basesoc_arty_vivado/gateware/top.bit \
		>soc_basesoc_arty_vivado.fasm \
		|| (rm -f soc_basesoc_arty_vivado.fasm && exit -1)

