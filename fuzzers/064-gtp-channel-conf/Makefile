# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

SHELL = bash

N ?= 10

BUILD_DIR = build_${XRAY_PART}

SPECIMENS := $(addprefix ${BUILD_DIR}/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
FUZDIR ?= ${PWD}


all: database

$(SPECIMENS_OK): $(SPECIMENS_DEPS)
	mkdir -p ${BUILD_DIR}
	bash ${XRAY_DIR}/utils/top_generate.sh $(subst /OK,,$@)

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.${XRAY_PART}.ok

clean:
	rm -rf ${BUILD_DIR} run.${XRAY_PART}.ok

.PHONY: all run clean

database: ${BUILD_DIR}/segbits_gtp_channelx.db

${BUILD_DIR}/segbits_gtp_channelx.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -c 9 -o ${BUILD_DIR}/segbits_gtp_channelx.rdb $$(find $(SPECIMENS) -name "segdata_gtp_channel_[0123]*")

${BUILD_DIR}/segbits_gtp_channelx.db: ${BUILD_DIR}/segbits_gtp_channelx.rdb
	${XRAY_DBFIXUP} --db-root ${BUILD_DIR} --zero-db bits.dbf \
		--seg-fn-in ${BUILD_DIR}/segbits_gtp_channelx.rdb \
		--seg-fn-out ${BUILD_DIR}/segbits_gtp_channelx.db
	${XRAY_MASKMERGE} ${BUILD_DIR}/mask_gtp_channelx.db $$(find $(SPECIMENS) -name "segdata_gtp_channel_[0123]*")

pushdb:
	BUILD_DIR=$(BUILD_DIR) source pushdb.sh

.PHONY: database pushdb
