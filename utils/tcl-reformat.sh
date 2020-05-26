#!/usr/bin/env bash
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
# Wrapper to clean up newlines
# We could do this in tcl...but tcl

fn=$1

third_party/reformat.tcl $fn >/dev/null
# Always puts a newline at the end, even if there was one before
# remove duplicates, but keep at least one
printf "%s\n" "$(< $fn)" >$fn.tmp
mv $fn.tmp $fn

# Remove trailing spaces
sed -i 's/[ \t]*$//' "$fn"

