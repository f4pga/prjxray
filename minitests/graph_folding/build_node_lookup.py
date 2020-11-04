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

import argparse
import progressbar

from prjxray import util
from prjxray.db import Database
from node_lookup import NodeLookup
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('database')
    util.db_root_arg(parser)
    util.part_arg(parser)

    args = parser.parse_args()

    db = Database(args.db_root, args.part)

    if os.path.exists(args.database):
        os.unlink(args.database)

    lookup = NodeLookup(database=args.database)
    try:
        lookup.build_database(db, progressbar.progressbar)
    except Exception:
        os.unlink(args.database)
        raise


if __name__ == "__main__":
    main()
