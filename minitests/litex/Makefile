YOSYS_PATH = $(PWD)/yosys
CROSS_TOOL = $(PWD)/crosstool-ng/riscv32-unknown-elf/bin
LITEX_ARGS = --cpu-type vexriscv --with-ethernet --no-compile-software

all: soc_basesoc_arty_yosys soc_basesoc_arty_vivado

clean:
	rm -f yosys/yosys
	rm -f crosstool-ng/toolchain.ok
	rm -rf soc_basesoc_arty_yosys
	rm -rf soc_basesoc_arty_vivado

.PHONY: all clean soc_basesoc_arty_yosys soc_basesoc_arty_vivado

#  ------------ toolchain -------------

crosstool-ng/build.ok:
	./build_toolchain.sh

yosys/yosys:
	./build_yosys.sh

# -------------- LiteX ----------------

soc_basesoc_arty_yosys: soc_basesoc_arty_yosys/software soc_basesoc_arty_yosys/gateware/top.bit 

soc_basesoc_arty_vivado: soc_basesoc_arty_vivado/software soc_basesoc_arty_vivado/gateware/top.bit

soc_basesoc_arty_yosys/software soc_basesoc_arty_yosys/gateware/top.bit: crosstool-ng/build.ok yosys/yosys
	PYTHONPATH="$(PWD)/migen:$(PWD)/litex:$(PWD)/litedram:$(PWD)/liteeth" \
	PATH="$(YOSYS_PATH):$(CROSS_TOOL):$(PATH)" \
	python3 \
		litex/litex/boards/targets/arty.py \
        --synth-mode "yosys" \
		--output-dir=soc_basesoc_arty_yosys \
		$(LITEX_ARGS)

soc_basesoc_arty_vivado/software soc_basesoc_arty_vivado/gateware/top.bit: crosstool-ng/build.ok
	PYTHONPATH="$(PWD)/migen:$(PWD)/litex:$(PWD)/litedram:$(PWD)/liteeth" \
	PATH="$(YOSYS_PATH):$(CROSS_TOOL):$(PATH)" \
	python3 \
		litex/litex/boards/targets/arty.py \
        --synth-mode "vivado" \
		--output-dir=soc_basesoc_arty_vivado \
		$(LITEX_ARGS)
