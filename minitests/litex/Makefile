#YOSYS = /home/tmichalak/Development/X-Ray/yosys
CROSS_TOOL = $(PWD)/crosstool-ng/riscv32-unknown-elf/bin
LITEX_ARGS = --cpu-type vexriscv --with-ethernet --no-compile-software 

all: crosstool-ng/build.ok
	@echo $$(PWD)
clean:
	rm toolchain.ok


#  ------------ toolchain -------------
crosstool-ng/build.ok:
	./build_toolchain.sh

build-yosys:
	./build_yosys.sh

litex/yosys: crosstool-ng/build.ok
	PYTHONPATH="$(PWD)/migen:$(PWD)/litex:$(PWD)/litedram:$(PWD)/liteeth" \
	PATH="$(YOSYS):$(CROSS_TOOL):$(PATH)" \
	python3 \
		litex/litex/boards/targets/arty.py \
		--output-dir=soc_basesoc_arty_yosys \
		$(LITEX_ARGS) --no-compile-gateware

litex/vivado: crosstool-ng/build.ok
	PYTHONPATH="$(PWD)/migen:$(PWD)/litex:$(PWD)/litedram:$(PWD)/liteeth" \
	PATH="$(YOSYS):$(CROSS_TOOL):$(PATH)" \
	python3 \
		litex/litex/boards/targets/arty.py \
		--output-dir=soc_basesoc_arty_vivado \
		$(LITEX_ARGS)
