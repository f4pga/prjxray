#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set -e
${XRAY_VIVADO} -mode batch -source runme.tcl
echo "=========================================================="
md5sum wires_{INT,CLBLL,CLBLM}_[LR]_*.txt | sed -re 's,X[0-9]+Y[0-9]+,XY,' | sort | uniq -c | sort -k3
echo "=========================================================="
md5sum pips_{INT,CLBLL,CLBLM}_[LR]_*.txt | sed -re 's,X[0-9]+Y[0-9]+,XY,' | sort | uniq -c | sort -k3
