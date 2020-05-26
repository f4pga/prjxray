#!/bin/bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

DATABASE=$1

# If DATABASE is empty, checks htmlgen for all settings files
SETTINGS=../settings/$DATABASE*.sh

for setting in $SETTINGS
do
    no_prefix_setting=${setting#../settings/}
    clean_setting=${no_prefix_setting%.sh}
    echo ""
    echo "============================================="
    echo "Generating HTML for ${clean_setting}"
    echo "============================================="
    echo ""
    source ../settings/$setting
    ./htmlgen.py --output html/${clean_setting}
done
