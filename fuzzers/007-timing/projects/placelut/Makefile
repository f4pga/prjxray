N := 1
SPECIMENS := $(addprefix specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
CSVS := $(addsuffix /timing3.csv,$(SPECIMENS))
TIMFUZ_DIR=$(XRAY_DIR)/fuzzers/007-timing

all: tilea.json

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

sub.json: $(SPECIMENS_OK)
	# Discover which variables can be separated
	# This is typically the longest running operation
	python3 $(TIMFUZ_DIR)/rref.py --simplify --out sub.json $(CSVS)

grouped.csv: $(SPECIMENS_OK) sub.json
	# Separate variables
	python3 $(TIMFUZ_DIR)/csv_flat2group.py --sub-json sub.json --strict $(CSVS) grouped.csv
	# Verify sub.json makes a solvable solution
	# python3 $(TIMFUZ_DIR)/checksub.py --sub-json sub.json grouped.csv

leastsq.csv: sub.json grouped.csv
	# Create a rough timing model that approximately fits the given paths
	python3 $(TIMFUZ_DIR)/solve_leastsq.py --sub-json sub.json grouped.csv --out leastsq.csv

linprog.csv: leastsq.csv grouped.csv
	# Tweak rough timing model, making sure all constraints are satisfied
	python3 $(TIMFUZ_DIR)/solve_linprog.py --sub-json sub.json --sub-csv leastsq.csv --massage grouped.csv --out linprog.csv

flat.csv: linprog.csv
	# Take separated variables and back-annotate them to the original timing variables
	python3 $(TIMFUZ_DIR)/csv_group2flat.py --sub-json sub.json --sort linprog.csv flat.csv

tilea.json: flat.csv
	# Final processing
	# Insert timing delays into actual tile layouts
	python3 $(TIMFUZ_DIR)/tile_annotate.py --tile-json $(TIMFUZ_DIR)/timgrid/build/timgrid.json flat.csv tilea.json

