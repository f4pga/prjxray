
N := 1
BUILD_DIR = build_${XRAY_PART}
SPECIMENS := $(addprefix $(BUILD_DIR)/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
MAX_VIVADO_PROCESS ?= 4
MAX_PIPS_INSTANCE ?= 340000

database: $(SPECIMENS_OK)
	true

pushdb:
	true

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@) -p=$(MAX_VIVADO_PROCESS) -t=$(MAX_PIPS_INSTANCE)
	touch $@

run:
	rm -rf $(BUILD_DIR) run.${XRAY_PART}.ok
	$(MAKE) database
	$(MAKE) pushdb
	touch run.${XRAY_PART}.ok

clean:
	rm -rf build_* run.*.ok

.PHONY: database pushdb run clean

