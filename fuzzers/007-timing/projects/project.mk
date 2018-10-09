# project.mk: build specimens (run vivado), compute rref
# corner.mk: run corner specific calculations

N := 1
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
TIMFUZ_DIR=$(XRAY_DIR)/fuzzers/007-timing
# Allow an empty system of equations?
# for testing only on small projects
ALLOW_ZERO_EQN?=N
# Constrained projects may fail to build
# Set to Y to make a best effort to suck in the ones that did build
BADPRJ_OK?=N
BUILD_DIR?=build
# interconnect
BUILD_DIR_I?=$(BUILD_DIR)/i
# site
BUILD_DIR_S?=$(BUILD_DIR)/s

CORNERS=fast_max fast_min slow_max slow_min

TIMGRID_V_I=$(BUILD_DIR_I)/timgrid-v.json
TIMGRID_V_S=$(BUILD_DIR_S)/timgrid-v.json

all: $(BUILD_DIR)/timgrid-v.json

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@) || (if [ "$(BADPRJ_OK)" != 'Y' ] ; then exit 1; fi; exit 0)
	touch $@

run:
	$(MAKE) clean
	$(MAKE) all
	touch run.ok

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_clblx.segbits __pycache__ run.ok
	rm -rf vivado*.log vivado_*.str vivado*.jou design *.bits *.dcp *.bit
	rm -rf $(BUILD_DIR)

.PHONY: all run clean

$(TIMGRID_V_I): $(SPECIMENS_OK)
	$(MAKE) -f $(TIMFUZ_DIR)/projects/is.mk BUILD_DIR=$(BUILD_DIR_I) SOLVING=i SPECIMENS=$(SPECIMENS) all
i: $(TIMGRID_V_I)

$(TIMGRID_V_S): $(SPECIMENS_OK)
	$(MAKE) -f $(TIMFUZ_DIR)/projects/is.mk BUILD_DIR=$(BUILD_DIR_S) SOLVING=s SPECIMENS=$(SPECIMENS) all
s: $(TIMGRID_V_S)

.PHONY: i s

$(BUILD_DIR)/timgrid-v.json: $(TIMGRID_V_I) $(TIMGRID_V_S)
	python3 $(TIMFUZ_DIR)/timgrid_vc2v.py --out $(BUILD_DIR)/timgrid-v.json $(TIMGRID_V_I) $(TIMGRID_V_S)

