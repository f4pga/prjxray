#!/usr/bin/env bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

GITHUB_PROTO=${1:-https}
GITHUB_URL=$GITHUB_PROTO://github.com/SymbiFlow/prjxray-db.git
rm -rf database
git clone $GITHUB_URL database
# Update files in the database from our version so fuzzers run correctly.
git checkout HEAD database
