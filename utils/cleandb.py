#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

import sys, re
import os
from prjxray import util


def run(globaldb, localdb, verbose=False):

    local_db_files = list()
    work_db_files = list()

    # get DB files

    global_entries = {}
    local_entries = {}
    final_entries = {}

    verbose and print("removing %s from %s" % (localdb, globaldb))
    # parse global db
    for line, (tag, bits, mode) in util.parse_db_lines(globaldb):
        global_entries[tag] = bits
    # parse local db
    for line, (tag, bits, mode) in util.parse_db_lines(localdb):
        local_entries[tag] = bits

    for entry in global_entries:
        if entry not in local_entries:
            final_entries[entry] = global_entries[entry]
        else:
            verbose and print("Removing entry %s" % entry)

    util.write_db_lines(globaldb, final_entries)


def main():

    import argparse

    parser = argparse.ArgumentParser(
        description="Remove partial DB from global DB")
    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument(
        '--localdb', action='store', help='Path to work database')
    parser.add_argument(
        '--globaldb', action='store', help='Path to global database')

    args = parser.parse_args()

    run(args.globaldb, args.localdb, args.verbose)


if __name__ == '__main__':
    main()
