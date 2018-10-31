all: $(OUT_DIFF)

$(OUT_DIFF): build/$(PRJL)/design.bits build/$(PRJR)/design.bits
	diff build/$(PRJL)/design.bits build/$(PRJR)/design.bits >$(OUT_DIFF) || true

build/$(PRJL)/design.bits:
	PROJECT=$(PRJL) bash runme.sh

build/$(PRJR)/design.bits:
	PROJECT=$(PRJR) bash runme.sh

