# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
all: database

include ../pip_list.mk

database: piplist

pushdb:
	true

run: database
	touch run.ok

clean:
	rm -rf build run.ok

.PHONY: all clean run database pushdb
