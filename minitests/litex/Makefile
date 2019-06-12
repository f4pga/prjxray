YOSYS = /home/tmichalak/Development/X-Ray/yosys
CROSS_TOOL = $(PWD)/ct/riscv32-unknown-elf/bin
LITEX_ARGS = --no-compile-software

all: toolchain.ok
	@echo $$(PWD)
clean:
	rm toolchain.ok


#  ------------ toolchain -------------
build-toolchain:
	./build_toolchain.sh

build-yosys:
	./build_yosys.sh

litex/yosys: build-toolchain
	PYTHONPATH="$(PWD)/migen:$(PWD)/litex:$(PWD)/litedram:$(PWD)/liteeth" \
	PATH="$(YOSYS):$(CROSS_TOOL):$(PATH)" \
	python3 \
		litex/litex/boards/targets/arty.py \
		--output-dir=soc_basesoc_arty_yosys \
		$(LITEX_ARGS)

litex/vivado: build-toolchain
	PYTHONPATH="$(PWD)/migen:$(PWD)/litex:$(PWD)/litedram:$(PWD)/liteeth" \
	PATH="$(YOSYS):$(CROSS_TOOL):$(PATH)" \
	python3 \
		litex/litex/boards/targets/arty.py \
		--output-dir=soc_basesoc_arty_vivado \
		$(LITEX_ARGS)
