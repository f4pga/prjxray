# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
ifeq ($(QUICK),Y)
N := 1
else
N := 10
endif

SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -m 5 -M 15 -o build/segbits_int_l.db $(addsuffix /segdata_int_l.txt,$(SPECIMENS))
	${XRAY_SEGMATCH} -m 5 -M 15 -o build/segbits_int_r.db $(addsuffix /segdata_int_r.txt,$(SPECIMENS))
# May be undersolved
ifneq ($(QUICK),Y)
	${XRAY_DBFIXUP} --db-root build --clb-int
endif

pushdb:
	${XRAY_MERGEDB} int_l build/segbits_int_l.db
	${XRAY_MERGEDB} int_r build/segbits_int_r.db

$(SPECIMENS_OK): build/todo.txt
	mkdir -p build
	+bash generate.sh $(subst /OK,,$@)
	touch $@

build/todo.txt:
	mkdir -p build
	echo "INT_L.GFAN0.GND_WIRE" >  build/todo.txt
	echo "INT_L.GFAN1.GND_WIRE" >> build/todo.txt
	echo "INT_R.GFAN0.GND_WIRE" >> build/todo.txt
	echo "INT_R.GFAN1.GND_WIRE" >> build/todo.txt

run:
	$(MAKE) clean
	$(MAKE) database
# May be undersolved
ifneq ($(QUICK),Y)
	$(MAKE) pushdb
endif
	touch run.ok

clean:
	rm -rf build run.ok

.PHONY: database pushdb run clean

