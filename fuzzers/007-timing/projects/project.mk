# project.mk: build specimens (run vivado), compute rref
# corner.mk: run corner specific calculations

N := 1
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
CSVS := $(addsuffix /timing3.csv,$(SPECIMENS))
TIMFUZ_DIR=$(XRAY_DIR)/fuzzers/007-timing
RREF_CORNER=slow_max

TILEA_JSONS=build/fast_max/tilea.json build/fast_min/tilea.json build/slow_max/tilea.json build/slow_min/tilea.json

all: $(TILEA_JSONS)

# make build/checksub first
build/fast_max/tilea.json: build/checksub
	$(MAKE) -f $(TIMFUZ_DIR)/projects/corner.mk CORNER=fast_max
build/fast_min/tilea.json: build/checksub
	$(MAKE) -f $(TIMFUZ_DIR)/projects/corner.mk CORNER=fast_min
build/slow_max/tilea.json: build/checksub
	$(MAKE) -f $(TIMFUZ_DIR)/projects/corner.mk CORNER=slow_max
build/slow_min/tilea.json: build/checksub
	$(MAKE) -f $(TIMFUZ_DIR)/projects/corner.mk CORNER=slow_min
fast_max: build/fast_max/tilea.json
fast_min: build/fast_min/tilea.json
slow_max: build/slow_max/tilea.json
slow_min: build/slow_min/tilea.json

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

run:
	$(MAKE) clean
	$(MAKE) all
	touch run.ok

clean:
	rm -rf specimen_[0-9][0-9][0-9]/ seg_clblx.segbits __pycache__ run.ok
	rm -rf vivado*.log vivado_*.str vivado*.jou design *.bits *.dcp *.bit
	rm -rf build

.PHONY: all run clean

# rref should be the same regardless of corner

build/sub.json: $(SPECIMENS_OK)
	mkdir -p build
	# Discover which variables can be separated
	# This is typically the longest running operation
	python3 $(TIMFUZ_DIR)/rref.py --corner $(RREF_CORNER) --simplify --out build/sub.json.tmp $(CSVS)
	mv build/sub.json.tmp build/sub.json

build/grouped.csv: $(SPECIMENS_OK) build/sub.json
	# Separate variables
	python3 $(TIMFUZ_DIR)/csv_flat2group.py --sub-json build/sub.json --strict --out build/grouped.csv.tmp $(CSVS)
	mv build/grouped.csv.tmp build/grouped.csv

build/checksub: build/grouped.csv build/sub.json
	# Verify sub.json makes a cleanly solvable solution with no non-pivot leftover
	python3 $(TIMFUZ_DIR)/checksub.py --sub-json build/sub.json build/grouped.csv
	touch build/checksub

