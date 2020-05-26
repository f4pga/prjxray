# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
N := 1
SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)

pushdb: build/ps7_ports.json
	mkdir -p ${XRAY_FAMILY_DIR}
	cp build/ps7*.json ${XRAY_FAMILY_DIR}/

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

build/ps7_pins.csv: $(SPECIMENS_OK)
	cp build/specimen_001/ps7_pins.csv build/

build/ps7_ports.json: build/ps7_pins.csv
	python3 make_ports.py $< $@

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf build run.ok

.PHONY: database pushdb run clean
