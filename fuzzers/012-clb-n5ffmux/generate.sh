#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set -ex
if [ $(${XRAY_VIVADO} -h |grep Vivado |cut -d\  -f 2) != "v2017.2" ] ; then echo "FIXME: requires Vivado 2017.2. See https://github.com/SymbiFlow/prjxray/issues/14"; exit 1; fi
source ${XRAY_DIR}/utils/top_generate.sh

