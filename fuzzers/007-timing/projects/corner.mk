# Run corner specific calculations

TIMFUZ_DIR=$(XRAY_DIR)/fuzzers/007-timing
CORNER=slow_max
ALLOW_ZERO_EQN?=N
BADPRJ_OK?=N
BUILD_DIR?=build/MUST_SET
CSV_BASENAME=timing4i.csv

all: $(BUILD_DIR)/$(CORNER)/timgrid-vc.json $(BUILD_DIR)/$(CORNER)/qor.txt

run:
	$(MAKE) clean
	$(MAKE) all
	touch run.ok

clean:
	rm -rf $(BUILD_DIR)/$(CORNER)

.PHONY: all run clean

$(BUILD_DIR)/$(CORNER):
	mkdir -p $(BUILD_DIR)/$(CORNER)

# parent should have built this
$(BUILD_DIR)/checksub:
	false

$(BUILD_DIR)/$(CORNER)/leastsq.csv: $(BUILD_DIR)/sub.json $(BUILD_DIR)/grouped.csv $(BUILD_DIR)/checksub $(BUILD_DIR)/$(CORNER)
	# Create a rough timing model that approximately fits the given paths
	python3 $(TIMFUZ_DIR)/solve_leastsq.py $(BUILD_DIR)/grouped.csv --corner $(CORNER) --out $(BUILD_DIR)/$(CORNER)/leastsq.csv.tmp
	mv $(BUILD_DIR)/$(CORNER)/leastsq.csv.tmp $(BUILD_DIR)/$(CORNER)/leastsq.csv

$(BUILD_DIR)/$(CORNER)/linprog.csv: $(BUILD_DIR)/$(CORNER)/leastsq.csv $(BUILD_DIR)/grouped.csv
	# Tweak rough timing model, making sure all constraints are satisfied
	ALLOW_ZERO_EQN=$(ALLOW_ZERO_EQN) python3 $(TIMFUZ_DIR)/solve_linprog.py --bounds-csv $(BUILD_DIR)/$(CORNER)/leastsq.csv --massage $(BUILD_DIR)/grouped.csv --corner $(CORNER) --out $(BUILD_DIR)/$(CORNER)/linprog.csv.tmp
	mv $(BUILD_DIR)/$(CORNER)/linprog.csv.tmp $(BUILD_DIR)/$(CORNER)/linprog.csv

$(BUILD_DIR)/$(CORNER)/flat.csv: $(BUILD_DIR)/$(CORNER)/linprog.csv
	# Take separated variables and back-annotate them to the original timing variables
	python3 $(TIMFUZ_DIR)/csv_group2flat.py --sub-json $(BUILD_DIR)/sub.json --corner $(CORNER) --out $(BUILD_DIR)/$(CORNER)/flat.csv.tmp $(BUILD_DIR)/$(CORNER)/linprog.csv
	mv $(BUILD_DIR)/$(CORNER)/flat.csv.tmp $(BUILD_DIR)/$(CORNER)/flat.csv

$(BUILD_DIR)/$(CORNER)/timgrid-vc.json: $(BUILD_DIR)/$(CORNER)/flat.csv
	# Final processing
	# Insert timing delays into actual tile layouts
	python3 $(TIMFUZ_DIR)/tile_annotate.py --timgrid-s $(TIMFUZ_DIR)/timgrid/build/timgrid-s.json --out $(BUILD_DIR)/$(CORNER)/timgrid-vc.json $(BUILD_DIR)/$(CORNER)/flat.csv

$(BUILD_DIR)/$(CORNER)/qor.txt: $(BUILD_DIR)/$(CORNER)/flat.csv
ifeq ($(SOLVING),i)
	python3 $(TIMFUZ_DIR)/solve_qor.py --corner $(CORNER) --bounds-csv $(BUILD_DIR)/$(CORNER)/flat.csv specimen_*/timing4i.csv >$(BUILD_DIR)/$(CORNER)/qor.txt.tmp
	mv $(BUILD_DIR)/$(CORNER)/qor.txt.tmp $(BUILD_DIR)/$(CORNER)/qor.txt
else
    # FIXME
	touch $(BUILD_DIR)/$(CORNER)/qor.txt
endif

