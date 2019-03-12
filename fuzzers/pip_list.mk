PIP_TYPE?=pips_int
A_PIPLIST?=$(PIP_TYPE)_l.txt
PIPLIST_TCL?=$(XRAY_FUZZERS_DIR)/piplist/piplist.tcl

$(XRAY_FUZZERS_DIR)/piplist/build/$(PIP_TYPE)/$(A_PIPLIST): $(PIPLIST_TCL)
	mkdir -p $(XRAY_FUZZERS_DIR)/piplist/build/$(PIP_TYPE)
	cd $(XRAY_FUZZERS_DIR)/piplist/build/$(PIP_TYPE) && ${XRAY_VIVADO} -mode batch -source $(PIPLIST_TCL)

piplist: $(XRAY_FUZZERS_DIR)/piplist/build/$(PIP_TYPE)/$(A_PIPLIST)

cleanpiplist:
	rm -rf $(XRAY_FUZZERS_DIR)/piplist/build

.PHONY: piplist cleanpiplist
