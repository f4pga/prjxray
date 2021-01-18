# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

SHELL = bash

N ?= 20

SPECIMENS := $(addprefix build/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
FUZDIR ?= ${PWD}

all: database

# generate.sh / top_generate.sh call make, hence the command must
# have a + before it.
$(SPECIMENS_OK): $(SPECIMENS_DEPS)
	mkdir -p build
	bash ${XRAY_DIR}/utils/top_generate.sh $(subst /OK,,$@)

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.${XRAY_PART}.ok

clean:
	rm -rf build run.ok

.PHONY: all run clean

database: build/segbits_gtp_common.db

build/segbits_gtp_common.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_gtp_common.rdb $$(find $(SPECIMENS) -name "segdata_gtp_common*")

build/segbits_gtp_common.db: build/segbits_gtp_common.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf \
		--seg-fn-in build/segbits_gtp_common.rdb \
		--seg-fn-out build/segbits_gtp_common.db
	${XRAY_MASKMERGE} build/mask_gtp_common.db $$(find $(SPECIMENS) -name "segdata_gtp_common*")

pushdb:
	source pushdb.sh

.PHONY: database pushdb
