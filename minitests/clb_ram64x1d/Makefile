N := 3
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

all: top.v
	bash runme.sh
	test -z $(fgrep CRITICAL vivado.log)
	${XRAY_SEGPRINT} -z -D design.bits  >design.txt

top.v: top.py
	python top.py >top.v

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o seg_clblx.segbits $(addsuffix /segdata_clbl[lm]_[lr].txt,$(SPECIMENS))

pushdb:
	${XRAY_MERGEDDB} clbll_l seg_clblx.segbits
	${XRAY_MERGEDDB} clbll_r seg_clblx.segbits
	${XRAY_MERGEDDB} clblm_l seg_clblx.segbits
	${XRAY_MERGEDDB} clblm_r seg_clblx.segbits

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_clblx.segbits vivado*.log vivado_*.str vivado*.jou design *.bits *.dcp *.bit design.txt .Xil

.PHONY: database pushdb clean

