# Interconnect and site (IS) high level aggregation
# Creates corner data and aggregates them together

TIMFUZ_DIR=$(XRAY_DIR)/fuzzers/007-timing
SOLVING=i
CSV_BASENAME=timing4$(SOLVING).csv
BUILD_DIR?=build/MUST_SET
SPECIMENS :=
CSVS := $(addsuffix /$(CSV_BASENAME),$(SPECIMENS))
RREF_CORNER=slow_max

# Set ZERO elements to zero delay (as is expected they should be)
RMZERO?=N

RREF_ARGS=
ifeq ($(RMZERO),Y)
RREF_ARGS+=--rm-zero
endif


# FIXME: clean this up by generating targets from CORNERS

# fast_max => build/i/fast_max/timgrid-vc.json
TIMGRID_VCS=$(BUILD_DIR)/fast_max/timgrid-vc.json $(BUILD_DIR)/fast_min/timgrid-vc.json $(BUILD_DIR)/slow_max/timgrid-vc.json $(BUILD_DIR)/slow_min/timgrid-vc.json
#TIMGRID_VCS=$(addsuffix /timgrid-vc.json,$(addprefix $(BUILD_DIR_I)/,$(CORNERS)))
# make $(BUILD_DIR)/checksub first
$(BUILD_DIR)/fast_max/timgrid-vc.json: $(BUILD_DIR)/checksub
	$(MAKE) -f $(TIMFUZ_DIR)/projects/corner.mk CORNER=fast_max
$(BUILD_DIR)/fast_min/timgrid-vc.json: $(BUILD_DIR)/checksub
	$(MAKE) -f $(TIMFUZ_DIR)/projects/corner.mk CORNER=fast_min
$(BUILD_DIR)/slow_max/timgrid-vc.json: $(BUILD_DIR)/checksub
	$(MAKE) -f $(TIMFUZ_DIR)/projects/corner.mk CORNER=slow_max
$(BUILD_DIR)/slow_min/timgrid-vc.json: $(BUILD_DIR)/checksub
	$(MAKE) -f $(TIMFUZ_DIR)/projects/corner.mk CORNER=slow_min


# Normally require all projects to complete
# If BADPRJ_OK is allowed, only take projects that were successful
# FIXME: couldn't get call to work
exist_csvs = \
        for f in $(CSVS); do \
            if [ "$(BADPRJ_OK)" != 'Y' -o -f $$f ] ; then \
                echo $$f; \
            fi; \
        done

all: $(BUILD_DIR)/timgrid-v.json

# rref should be the same regardless of corner
$(BUILD_DIR)/sub.json: $(SPECIMENS_OK)
	mkdir -p $(BUILD_DIR)
	# Discover which variables can be separated
	# This is typically the longest running operation
	\
	    csvs=$$(for f in $(CSVS); do if [ "$(BADPRJ_OK)" != 'Y' -o -f $$f ] ; then echo $$f; fi; done) ; \
	    echo $$csvs ; \
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

