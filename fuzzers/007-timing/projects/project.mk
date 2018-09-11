N := 1
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
CSVS := $(addsuffix /timing3.csv,$(SPECIMENS))
TIMFUZ_DIR=$(XRAY_DIR)/fuzzers/007-timing

all: build/tilea.json

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

.PHONY: database pushdb run clean

build/sub.json: $(SPECIMENS_OK)
	mkdir -p build
	# Discover which variables can be separated
	# This is typically the longest running operation
	python3 $(TIMFUZ_DIR)/rref.py --simplify --out build/sub.json.tmp $(CSVS)
	mv build/sub.json.tmp build/sub.json

build/grouped.csv: $(SPECIMENS_OK) build/sub.json
	# Separate variables
	python3 $(TIMFUZ_DIR)/csv_flat2group.py --sub-json build/sub.json --strict --out build/grouped.csv.tmp $(CSVS)
	mv build/grouped.csv.tmp build/grouped.csv

build/checksub: build/grouped.csv build/sub.json
	# Verify sub.json makes a cleanly solvable solution with no non-pivot leftover
	python3 $(TIMFUZ_DIR)/checksub.py --sub-json build/sub.json build/grouped.csv
	touch build/checksub

build/leastsq.csv: build/sub.json build/grouped.csv build/checksub
	# Create a rough timing model that approximately fits the given paths
	python3 $(TIMFUZ_DIR)/solve_leastsq.py --sub-json build/sub.json build/grouped.csv --out build/leastsq.csv.tmp
	mv build/leastsq.csv.tmp build/leastsq.csv

build/linprog.csv: build/leastsq.csv build/grouped.csv
	# Tweak rough timing model, making sure all constraints are satisfied
	python3 $(TIMFUZ_DIR)/solve_linprog.py --sub-json build/sub.json --sub-csv build/leastsq.csv --massage build/grouped.csv --out build/linprog.csv.tmp
	mv build/linprog.csv.tmp build/linprog.csv

build/flat.csv: build/linprog.csv
	# Take separated variables and back-annotate them to the original timing variables
	python3 $(TIMFUZ_DIR)/csv_group2flat.py --sub-json build/sub.json --sort build/linprog.csv build/flat.csv.tmp
	mv build/flat.csv.tmp build/flat.csv

build/tilea.json: build/flat.csv
	# Final processing
	# Insert timing delays into actual tile layouts
	python3 $(TIMFUZ_DIR)/tile_annotate.py --tile-json $(TIMFUZ_DIR)/timgrid/build/timgrid.json build/flat.csv build/tilea.json

