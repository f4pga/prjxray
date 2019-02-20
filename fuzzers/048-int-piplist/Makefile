PIP_TYPE?=pips_int
A_PIPLIST?=$(PIP_TYPE)_l.txt
PIPLIST_TCL?=$(XRAY_FUZZERS_DIR)/piplist/piplist.tcl

all: database

database: $(XRAY_FUZZERS_DIR)/piplist/build/$(A_PIPLIST)

$(XRAY_FUZZERS_DIR)/piplist/build/$(A_PIPLIST): $(PIPLIST_TCL)
	mkdir -p $(XRAY_FUZZERS_DIR)/piplist/build
	cd $(XRAY_FUZZERS_DIR)/piplist/build && ${XRAY_VIVADO} -mode batch \
		-source $(PIPLIST_TCL)


pushdb:
	true

run: database
	touch run.ok

clean:
	rm -rf build run.ok

cleanpiplist:
	rm -rf $(XRAY_FUZZERS_DIR)/piplist/build

.PHONY: all clean cleanpiplist run database pushdb

