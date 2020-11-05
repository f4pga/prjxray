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

from prjxray import util
from prjxray.db import Database


def main():
    parser = argparse.ArgumentParser()
    util.db_root_arg(parser)
    util.part_arg(parser)

    args = parser.parse_args()

    db = Database(args.db_root, args.part)

    for tile_type in sorted(db.get_tile_types()):
        print(tile_type)


if __name__ == "__main__":
    main()
