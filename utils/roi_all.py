#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2021  The Project X-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
import argparse
import yaml
import subprocess
import os
import re
from prjxray import util


def main():
    """Rois all parts for a family by calling "make roi_only" over all parts
    with the same device as XRAY_PART.

    Example:
        prjxray$ ./utils/roi_all.py --db-root database/artix7/ --part xc7a100tfgg676-1
    """
    env = os.environ.copy()
    db_root = util.get_db_root()
    assert db_root
    part = util.get_part()
    assert part

    information = util.get_part_information(db_root, part)

    valid_devices = []
    for name, device in util.get_devices(db_root).items():
        if device['fabric'] == information['device']:
            valid_devices.append(name)

    for part, data in util.get_parts(db_root).items():
        if data['device'] in valid_devices:
            command = "make roi_only"
            env['XRAY_PART'] = part
            cwd = os.getenv('XRAY_FUZZERS_DIR')
            subprocess.run(command.split(' '), check=True, env=env, cwd=cwd)


if __name__ == '__main__':
    main()
