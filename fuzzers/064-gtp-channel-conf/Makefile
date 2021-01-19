# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
N ?= 40

include ../fuzzer.mk

database: build/segbits_gtp_channelx.db

build/segbits_gtp_channelx.rdb: $(SPECIMENS_OK)
	${XRAY_SEGMATCH} -o build/segbits_gtp_channelx.rdb $(addsuffix /segdata_gtp_channel_[0123].txt,$(SPECIMENS))

build/segbits_gtp_channelx.db: build/segbits_gtp_channelx.rdb
	${XRAY_DBFIXUP} --db-root build --zero-db bits.dbf --seg-fn-in $^ --seg-fn-out $@
	${XRAY_MASKMERGE} build/mask_gtp_channelx.db $(addsuffix /segdata_gtp_channel_[0123].txt,$(SPECIMENS))

pushdb:
	${XRAY_MERGEDB} gtp_channel_0 build/segbits_gtp_channelx.db
	${XRAY_MERGEDB} gtp_channel_1 build/segbits_gtp_channelx.db
	${XRAY_MERGEDB} gtp_channel_2 build/segbits_gtp_channelx.db
	${XRAY_MERGEDB} gtp_channel_3 build/segbits_gtp_channelx.db
	${XRAY_MERGEDB} mask_gtp_channel_0 build/mask_gtp_channelx.db
	${XRAY_MERGEDB} mask_gtp_channel_1 build/mask_gtp_channelx.db
	${XRAY_MERGEDB} mask_gtp_channel_2 build/mask_gtp_channelx.db
	${XRAY_MERGEDB} mask_gtp_channel_3 build/mask_gtp_channelx.db

.PHONY: database pushdb
