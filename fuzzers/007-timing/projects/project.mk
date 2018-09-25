# project.mk: build specimens (run vivado), compute rref
# corner.mk: run corner specific calculations

N := 1
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
CSVS := $(addsuffix /timing4i.csv,$(SPECIMENS))
TIMFUZ_DIR=$(XRAY_DIR)/fuzzers/007-timing
RREF_CORNER=slow_max
# Allow an empty system of equations?
# for testing only on small projects
ALLOW_ZERO_EQN?=N
# Constrained projects may fail to build
# Set to Y to make a best effort to suck in the ones that did build
BADPRJ_OK?=N
# Set ZERO elements to zero delay (as is expected they should be)
RMZERO?=N
BUILD_DIR?=build

RREF_ARGS=
ifeq ($(RMZERO),Y)
RREF_ARGS+=--rm-zero
endif

TIMGRID_VCS=$(BUILD_DIR)/fast_max/timgrid-vc.json $(BUILD_DIR)/fast_min/timgrid-vc.json $(BUILD_DIR)/slow_max/timgrid-vc.json $(BUILD_DIR)/slow_min/timgrid-vc.json

all: $(BUILD_DIR)/timgrid-v.json

# make $(BUILD_DIR)/checksub first
$(BUILD_DIR)/fast_max/timgrid-vc.json: $(BUILD_DIR)/checksub
	$(MAKE) -f $(TIMFUZ_DIR)/projects/corner.mk CORNER=fast_max
$(BUILD_DIR)/fast_min/timgrid-vc.json: $(BUILD_DIR)/checksub
	$(MAKE) -f $(TIMFUZ_DIR)/projects/corner.mk CORNER=fast_min
$(BUILD_DIR)/slow_max/timgrid-vc.json: $(BUILD_DIR)/checksub
	$(MAKE) -f $(TIMFUZ_DIR)/projects/corner.mk CORNER=slow_max
$(BUILD_DIR)/slow_min/timgrid-vc.json: $(BUILD_DIR)/checksub
	$(MAKE) -f $(TIMFUZ_DIR)/projects/corner.mk CORNER=slow_min

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

# Normally require all projects to complete
# If BADPRJ_OK is allowed, only take projects that were successful
# FIXME: couldn't get call to work
exist_csvs = \
        for f in $(CSVS); do \
            if [ "$(BADPRJ_OK)" != 'Y' -o -f $$f ] ; then \
                echo $$f; \
            fi; \
        done

# rref should be the same regardless of corner
$(BUILD_DIR)/sub.json: $(SPECIMENS_OK)
	mkdir -p $(BUILD_DIR)
	# Discover which variables can be separated
	# This is typically the longest running operation
	\
	    csvs=$$(for f in $(CSVS); do if [ "$(BADPRJ_OK)" != 'Y' -o -f $$f ] ; then echo $$f; fi; done) ; \
	    python3 $(TIMFUZ_DIR)/rref.py --corner $(RREF_CORNER) --simplify $(RREF_ARGS) --out $(BUILD_DIR)/sub.json.tmp $$csvs
	mv $(BUILD_DIR)/sub.json.tmp $(BUILD_DIR)/sub.json

$(BUILD_DIR)/grouped.csv: $(SPECIMENS_OK) $(BUILD_DIR)/sub.json
	# Separate variables
	\
	    csvs=$$(for f in $(CSVS); do if [ "$(BADPRJ_OK)" != 'Y' -o -f $$f ] ; then echo $$f; fi; done) ; \
	    python3 $(TIMFUZ_DIR)/csv_flat2group.py --sub-json $(BUILD_DIR)/sub.json --strict --out $(BUILD_DIR)/grouped.csv.tmp $$csvs
	mv $(BUILD_DIR)/grouped.csv.tmp $(BUILD_DIR)/grouped.csv

$(BUILD_DIR)/checksub: $(BUILD_DIR)/grouped.csv $(BUILD_DIR)/sub.json
	# Verify sub.json makes a cleanly solvable solution with no non-pivot leftover
	python3 $(TIMFUZ_DIR)/checksub.py --sub-json $(BUILD_DIR)/sub.json $(BUILD_DIR)/grouped.csv
	touch $(BUILD_DIR)/checksub

$(BUILD_DIR)/timgrid-v.json: $(TIMGRID_VCS)
	python3 $(TIMFUZ_DIR)/timgrid_vc2v.py --out $(BUILD_DIR)/timgrid-v.json $(TIMGRID_VCS)

